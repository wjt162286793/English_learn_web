#!/usr/bin/env python3
"""Generate static course audio with the local kokorosay CLI."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "data"
AUDIO_DIR = ROOT / "public" / "audio"

STRING = r"""(['"])((?:\\.|(?!\1).)*)\1"""
LINE_PATTERN = re.compile(
    rf"line\(\s*{STRING}\s*,\s*{STRING}\s*,\s*{STRING}(?:\s*,\s*{STRING})?\s*\)",
    re.DOTALL,
)
SENTENCE_PATTERN = re.compile(
    rf"\{{\s*id:\s*{STRING}\s*,\s*textEn:\s*{STRING}",
    re.DOTALL,
)


def decode(quote: str, value: str) -> str:
    return ast.literal_eval(f"{quote}{value}{quote}")


def collect_lines() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    seen: set[str] = set()

    for source in sorted(DATA_DIR.glob("*.ts")):
        text = source.read_text(encoding="utf-8")
        for match in LINE_PATTERN.finditer(text):
            groups = match.groups()
            item_id = decode(groups[0], groups[1])
            if item_id in seen:
                continue
            seen.add(item_id)
            result.append(
                {
                    "id": item_id,
                    "text": decode(groups[2], groups[3]).replace("**", ""),
                    "speaker": decode(groups[6], groups[7]) if groups[6] else "",
                }
            )
        for match in SENTENCE_PATTERN.finditer(text):
            groups = match.groups()
            item_id = decode(groups[0], groups[1])
            if item_id in seen:
                continue
            seen.add(item_id)
            result.append(
                {
                    "id": item_id,
                    "text": decode(groups[2], groups[3]).replace("**", ""),
                    "speaker": "",
                }
            )

    speaker_order: dict[str, list[str]] = {}
    for item in result:
        dialogue_match = re.match(r"(.+-d\d+)-l\d+$", item["id"])
        if not dialogue_match or not item["speaker"]:
            continue
        group_id = dialogue_match.group(1)
        speaker_order.setdefault(group_id, [])
        if item["speaker"] not in speaker_order[group_id]:
            speaker_order[group_id].append(item["speaker"])

    for item in result:
        dialogue_match = re.match(r"(.+-d\d+)-l\d+$", item["id"])
        if not dialogue_match or not item["speaker"]:
            item["role"] = "female"
            continue
        speakers = speaker_order[dialogue_match.group(1)]
        item["role"] = "male" if speakers.index(item["speaker"]) % 2 else "female"

    return result


def apply_mode(text: str, mode: str) -> str:
    if mode == "standard":
        return text
    replacements = {
        "going to": "gonna",
        "want to": "wanna",
        "got to": "gotta",
        "have to": "hafta",
        "kind of": "kinda",
        "out of": "outta",
        "let me": "lemme",
        "give me": "gimme",
        "did you": "didja",
        "would you": "wouldja",
        "could you": "couldja",
    }
    result = text
    for source, target in replacements.items():
        result = re.sub(rf"\b{source}\b", target, result, flags=re.IGNORECASE)
    if mode == "dictation":
        result = re.sub(r"\bwhat do you\b", "whaddaya", result, flags=re.IGNORECASE)
        result = re.sub(r"\bwhat are you\b", "whatcha", result, flags=re.IGNORECASE)
        result = re.sub(r"\bdo you\b", "d'ya", result, flags=re.IGNORECASE)
    return result


def generate(mode: str, voice_map: dict[str, str], dry_run: bool) -> list[str]:
    generated: list[str] = []
    for item in collect_lines():
        role = item["role"]
        relative_path = Path("audio") / mode / f"{item['id']}-{role}.mp3"
        output_path = ROOT / "public" / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            "kokorosay",
            apply_mode(item["text"], mode),
            str(output_path),
            "--voice",
            voice_map[role],
        ]
        print(" ".join(command))
        if not dry_run:
            subprocess.run(command, check=True)
        generated.append(f"/{relative_path.as_posix()}")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("standard", "natural", "dictation", "all"),
        default="standard",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    modes = ("standard", "natural", "dictation") if args.mode == "all" else (args.mode,)
    voices = {"female": "af_heart", "male": "am_adam"}
    manifest: list[str] = []
    for mode in modes:
        manifest.extend(generate(mode, voices, args.dry_run))

    manifest_path = AUDIO_DIR / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        manifest_path.write_text(
            json.dumps(sorted(manifest), ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {len(manifest)} audio paths to {manifest_path}")


if __name__ == "__main__":
    main()
