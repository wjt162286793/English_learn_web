#!/usr/bin/env python3
"""Generate static Kokoro audio for the English learning app.

The site is a pure static frontend. This script reads the English content out of
``src/data``, synthesises it locally with Kokoro (ONNX build, no torch needed)
and writes MP3 files into ``public/audio``. It also (re)builds
``public/audio/manifest.json`` from the files that actually exist on disk, so the
frontend can tell which lines already have a static recording.

Examples
--------
    python scripts/generate_audio.py --mode all --dry-run
    python scripts/generate_audio.py --mode standard
    python scripts/generate_audio.py --mode all --force
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "data"
AUDIO_ROOT = PROJECT_ROOT / "public" / "audio"
MANIFEST_PATH = AUDIO_ROOT / "manifest.json"
MODEL_DIR = Path(__file__).resolve().parent / ".kokoro"

MODEL_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
    "model-files-v1.0/kokoro-v1.0.onnx"
)
VOICES_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
    "model-files-v1.0/voices-v1.0.bin"
)
MODEL_PATH = MODEL_DIR / "kokoro-v1.0.onnx"
VOICES_PATH = MODEL_DIR / "voices-v1.0.bin"

MODES: Tuple[str, ...] = ("standard", "natural", "dictation")
VOICE_BY_ROLE = {"female": "af_heart", "male": "am_adam"}

# Content files that always exist. ``builders.ts`` is a helpers-only module and
# is intentionally excluded. Any additional ``level*.ts`` file (for example a
# future ``level4a.ts``) is discovered automatically, so new content only needs
# to be dropped into ``src/data`` -- no code change required.
_REQUIRED_DATA_FILES = ("course.ts", "sentences.ts")


def discover_data_files() -> List[str]:
    """Return ``course.ts`` / ``sentences.ts`` plus every ``level*.ts`` file."""
    level_files = sorted(path.name for path in DATA_DIR.glob("level*.ts"))
    extra = [name for name in level_files if name not in _REQUIRED_DATA_FILES]
    return [*_REQUIRED_DATA_FILES, *extra]

# ---------------------------------------------------------------------------
# Pronunciation modes -- kept in sync with applyPronunciationMode() in App.vue
# ---------------------------------------------------------------------------

NATURAL_RULES: Sequence[Tuple[str, str]] = (
    (r"\bgoing to\b", "gonna"),
    (r"\bwant to\b", "wanna"),
    (r"\bgot to\b", "gotta"),
    (r"\bhave to\b", "hafta"),
    (r"\bkind of\b", "kinda"),
    (r"\bout of\b", "outta"),
    (r"\ba lot of\b", "a lotta"),
    (r"\blet me\b", "lemme"),
    (r"\bgive me\b", "gimme"),
    (r"\bdid you\b", "didja"),
    (r"\bwould you\b", "wouldja"),
    (r"\bcould you\b", "couldja"),
    (r"\bshould you\b", "shouldja"),
    (r"\bgot you\b", "gotcha"),
    (r"\bwant you to\b", "wantcha to"),
)

DICTATION_RULES: Sequence[Tuple[str, str]] = (
    (r"\bwhat do you\b", "whaddaya"),
    (r"\bwhat are you\b", "whatcha"),
    (r"\bdo you\b", "d'ya"),
    (r"\bare you\b", "are ya"),
    (r"\bdon't you\b", "doncha"),
    (r"\bhave you\b", "have ya"),
    (r"\bmeet you\b", "meetcha"),
    (r"\bget you\b", "getcha"),
)


def _capitalize_like(source: str, replacement: str) -> str:
    """Mirror capitalizeLike() in App.vue."""
    if not source:
        return replacement
    if source[0] == source[0].upper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _replace_phrase(text: str, pattern: str, replacement: str) -> str:
    return re.sub(
        pattern,
        lambda match: _capitalize_like(match.group(0), replacement),
        text,
        flags=re.IGNORECASE,
    )


def apply_natural(text: str) -> str:
    result = text
    for pattern, replacement in NATURAL_RULES:
        result = _replace_phrase(result, pattern, replacement)
    return result


def apply_dictation(text: str) -> str:
    result = apply_natural(text)
    for pattern, replacement in DICTATION_RULES:
        result = _replace_phrase(result, pattern, replacement)
    return result


def apply_mode(text: str, mode: str) -> str:
    if mode == "natural":
        return apply_natural(text)
    if mode == "dictation":
        return apply_dictation(text)
    return text


# ---------------------------------------------------------------------------
# Source parsing
# ---------------------------------------------------------------------------

_STRING = r"'(?:[^'\\]|\\.)*'"
_DSTRING = r'"(?:[^"\\]|\\.)*"'
# A single- or double-quoted JS string literal, quotes included.
_ANY_STRING = r"(?:" + _STRING + r"|" + _DSTRING + r")"
_LINE_CALL_RE = re.compile(
    r"\bline\(\s*"
    r"(" + _ANY_STRING + r")\s*,\s*"
    r"(" + _ANY_STRING + r")\s*,\s*"
    r"(" + _ANY_STRING + r")"
    r"(?:\s*,\s*(" + _ANY_STRING + r"))?\s*\)"
)
_TEMPLATE_RE = re.compile(r"const\s+(\w+)\s*=\s*`([\s\S]*?)`")
_PARSE_GROUP_RE = re.compile(
    r"parseGroup\(\s*(" + _STRING + r")\s*,\s*"
    + _STRING
    + r"\s*,\s*"
    + _STRING
    + r"\s*,\s*(\w+)\s*,?\s*\)"
)
_SENTENCE_ITEM_RE = re.compile(
    r"\{\s*id:\s*(" + _ANY_STRING + r")\s*,\s*textEn:\s*("
    + _ANY_STRING
    + r")\s*,\s*note:"
)
_SENTENCE_LINE_RE = re.compile(r"^(\d+)\.\s*(.+)\s+[\u2014\u2013]\s+(.+)$")

_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "'": "'", '"': '"', "\\": "\\", "`": "`", "0": "\0"}


def unescape_js(raw: str) -> str:
    """Turn a raw JS/TS string literal (including quotes) into plain text."""
    body = raw[1:-1]
    if "\\" not in body:
        return body
    out: List[str] = []
    index = 0
    length = len(body)
    while index < length:
        char = body[index]
        if char == "\\" and index + 1 < length:
            out.append(_ESCAPES.get(body[index + 1], body[index + 1]))
            index += 2
            continue
        out.append(char)
        index += 1
    return "".join(out)


def read_data_sources() -> Dict[str, str]:
    sources: Dict[str, str] = {}
    for name in discover_data_files():
        path = DATA_DIR / name
        if not path.exists():
            raise SystemExit(f"Missing course data file: {path}")
        sources[name] = path.read_text(encoding="utf-8")
    return sources


def extract_lines(sources: Dict[str, str]) -> List[dict]:
    """Extract every dialogue/article line declared through line(...)."""
    items: List[dict] = []
    for name, text in sources.items():
        for match in _LINE_CALL_RE.finditer(text):
            items.append(
                {
                    "id": unescape_js(match.group(1)),
                    "textEn": unescape_js(match.group(2)),
                    "textZh": unescape_js(match.group(3)),
                    "speaker": unescape_js(match.group(4)) if match.group(4) else "",
                    "source": name,
                }
            )
    return items


def extract_sentences(sources: Dict[str, str]) -> List[dict]:
    """Extract sentence drills, which use two different shapes in src/data."""
    items: List[dict] = []

    # sentences.ts keeps the drills inside template literals parsed by parseGroup().
    raw_text = sources.get("sentences.ts", "")
    templates = {name: body for name, body in _TEMPLATE_RE.findall(raw_text)}
    group_calls = list(_PARSE_GROUP_RE.finditer(raw_text))
    for call in group_calls:
        group_id = unescape_js(call.group(1))
        variable = call.group(2)
        body = templates.get(variable)
        if body is None:
            raise SystemExit(f"Could not find template literal for sentence group {variable}")
        for raw_line in body.split("\n"):
            line = raw_line.strip()
            if not line:
                continue
            match = _SENTENCE_LINE_RE.match(line)
            if not match:
                continue
            items.append(
                {
                    "id": f"{group_id}-s{match.group(1)}",
                    "textEn": match.group(2),
                    "source": "sentences.ts",
                }
            )
    if group_calls and not items:
        raise SystemExit("Failed to parse sentence drills from sentences.ts")

    # level2*/level3* declare the drills as plain object literals.
    for name, text in sources.items():
        if name == "sentences.ts":
            continue
        for match in _SENTENCE_ITEM_RE.finditer(text):
            items.append(
                {
                    "id": unescape_js(match.group(1)),
                    "textEn": unescape_js(match.group(2)),
                    "source": name,
                }
            )
    return items


def build_roles(lines: Iterable[dict]) -> Dict[str, str]:
    """Reproduce getDialogueVoiceRole() from App.vue for every line id."""
    sections: Dict[str, List[Tuple[int, str]]] = {}
    for item in lines:
        parts = item["id"].split("-")
        section = "-".join(parts[:4])
        line_no = int(parts[-1][1:])
        sections.setdefault(section, []).append((line_no, item["speaker"]))

    roles: Dict[str, str] = {}
    for section, entries in sections.items():
        entries.sort(key=lambda entry: entry[0])
        section_type = section.split("-")[3][0]
        speakers: List[str] = []
        for _, speaker in entries:
            if speaker and speaker not in speakers:
                speakers.append(speaker)

        for index, (_, speaker) in enumerate(entries):
            line_id = section + "-l" + str(entries[index][0])
            if section_type != "d" or not speaker:
                roles[line_id] = "female"
                continue
            speaker_index = speakers.index(speaker)
            if speaker_index == 1:
                roles[line_id] = "male"
            elif speaker_index >= 2:
                roles[line_id] = "female" if speaker_index % 2 == 0 else "male"
            else:
                roles[line_id] = "female"
    return roles


def build_tasks(modes: Sequence[str]) -> Tuple[List[dict], Dict[str, str]]:
    sources = read_data_sources()
    lines = extract_lines(sources)
    sentences = extract_sentences(sources)
    roles = build_roles(lines)

    tasks: List[dict] = []
    for item in lines:
        role = roles[item["id"]]
        key = f"{item['id']}-{role}"
        for mode in modes:
            tasks.append(
                {
                    "mode": mode,
                    "key": key,
                    "role": role,
                    "text": apply_mode(item["textEn"], mode),
                }
            )

    if "standard" in modes:
        # Sentence drills are always played from their raw text, so a single
        # recording per sentence is enough.
        for item in sentences:
            tasks.append(
                {
                    "mode": "standard",
                    "key": f"{item['id']}-female",
                    "role": "female",
                    "text": item["textEn"].replace("**", ""),
                }
            )

    stats = {
        "lines": str(len(lines)),
        "sentences": str(len(sentences)),
    }
    return tasks, stats


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


def ensure_models() -> Tuple[Path, Path]:
    import os

    model = Path(os.environ.get("KOKORO_MODEL", MODEL_PATH))
    voices = Path(os.environ.get("KOKORO_VOICES", VOICES_PATH))
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    _download(MODEL_URL, model)
    _download(VOICES_URL, voices)
    return model, voices


def _download(url: str, target: Path) -> None:
    if target.exists() and target.stat().st_size > 0:
        return
    print(f"Downloading {url}\n  -> {target}")
    tmp = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(url) as response, open(tmp, "wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    tmp.replace(target)
    print("Done.")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def write_mp3(path: Path, samples, sample_rate: int) -> None:
    import soundfile as sf

    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), samples, sample_rate, format="MP3")


def run_generation(tasks: Sequence[dict], force: bool, limit: Optional[int]) -> None:
    from kokoro_onnx import Kokoro

    model, voices = ensure_models()
    kokoro = Kokoro(str(model), str(voices))

    pending = []
    for task in tasks:
        out_path = AUDIO_ROOT / task["mode"] / f"{task['key']}.mp3"
        if out_path.exists() and not force:
            continue
        pending.append((task, out_path))
    if limit is not None:
        pending = pending[:limit]

    total = len(pending)
    if total == 0:
        print("Nothing to generate -- every target file already exists.")
        return

    print(f"Generating {total} file(s)...")
    failed: List[Tuple[str, str]] = []
    for index, (task, out_path) in enumerate(pending, 1):
        try:
            samples, sample_rate = kokoro.create(
                task["text"],
                voice=VOICE_BY_ROLE[task["role"]],
                speed=1.0,
                lang="en-us",
            )
            write_mp3(out_path, samples, sample_rate)
        except Exception as error:  # noqa: BLE001 - keep going, report at the end
            failed.append((str(out_path), str(error)))
        if index % 25 == 0 or index == total:
            print(f"  {index}/{total}")

    if failed:
        print(f"\n{len(failed)} file(s) failed:")
        for path, error in failed[:20]:
            print(f"  {path}: {error}")
        if len(failed) > 20:
            print(f"  ... and {len(failed) - 20} more")
    else:
        print("All files generated.")


def rebuild_manifest() -> List[str]:
    """List every MP3 that exists on disk as a site-absolute path."""
    paths: List[str] = []
    for mode in MODES:
        mode_dir = AUDIO_ROOT / mode
        if not mode_dir.is_dir():
            continue
        for mp3 in sorted(mode_dir.glob("*.mp3")):
            paths.append(f"/audio/{mode}/{mp3.name}")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(paths, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {MANIFEST_PATH.relative_to(PROJECT_ROOT)} ({len(paths)} file(s))")
    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--mode",
        choices=(*MODES, "all"),
        default="all",
        help="Which pronunciation mode to generate (default: all).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be generated.")
    parser.add_argument("--force", action="store_true", help="Regenerate files that already exist.")
    parser.add_argument("--limit", type=int, default=None, help="Only generate the first N files.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    modes = MODES if args.mode == "all" else (args.mode,)

    tasks, stats = build_tasks(modes)
    print(
        "Course data: "
        f"{stats['lines']} dialogue/article lines, {stats['sentences']} sentence drills"
    )
    print(f"Modes: {', '.join(modes)} -> {len(tasks)} planned file(s)")

    if args.dry_run:
        for task in tasks:
            out = (AUDIO_ROOT / task["mode"] / f"{task['key']}.mp3").relative_to(PROJECT_ROOT)
            print(
                f"kokoro-onnx --voice {VOICE_BY_ROLE[task['role']]} "
                f'--text "{task["text"]}" --out {out.as_posix()}'
            )
        existing = sum(1 for task in tasks if (AUDIO_ROOT / task["mode"] / f"{task['key']}.mp3").exists())
        print(f"\nDry run complete. {existing}/{len(tasks)} target file(s) already exist.")
        return 0

    run_generation(tasks, force=args.force, limit=args.limit)
    rebuild_manifest()
    return 0


if __name__ == "__main__":
    sys.exit(main())
