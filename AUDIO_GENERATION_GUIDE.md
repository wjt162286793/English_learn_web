# English Learning App 音频生成操作文档

本文档用于指导 AI 在本地为项目生成 Kokoro 静态英语音频。

## 目标

本项目是纯静态前端，不使用后端和在线 TTS API。

需要完成以下任务：

1. 安装本地 Kokoro TTS 工具。
2. 从项目课程数据中提取英文内容。
3. 生成标准版、口语连读版和听力辨音版 MP3。
4. 将 MP3 保存到 `public/audio/`。
5. 生成 `public/audio/manifest.json`。
6. 启动前端并验证音频优先播放。

浏览器会优先播放静态 MP3。某条音频不存在或播放失败时，前端会自动回退到浏览器语音。

## 项目目录

AI 必须在项目根目录执行命令。项目根目录应包含：

```text
package.json
src/
public/
scripts/generate_audio.py
```

先确认当前目录：

```bash
pwd
ls
```

如果不是项目根目录，请先进入项目目录：

```bash
cd /path/to/english-learning-app
```

## 环境要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- npm
- 可访问网络，用于第一次下载 Python 包和 Kokoro 模型
- 足够磁盘空间，建议至少预留 2 GB

检查环境：

```bash
python3 --version
node --version
npm --version
```

Windows 如果没有 `python3` 命令，可以使用：

```bash
python --version
```

## 安装依赖

先安装前端依赖：

```bash
npm install
```

再安装 Kokoro 命令行工具：

```bash
python3 -m pip install kokorosay
```

Windows 使用：

```bash
python -m pip install kokorosay
```

确认命令可用：

```bash
kokorosay --help
```

如果提示找不到 `kokorosay`，先关闭并重新打开终端，再执行一次。

如果仍然找不到，使用当前 Python 环境执行：

```bash
python3 -m pip show kokorosay
```

也可以先确认单句生成是否正常：

```bash
kokorosay "Hello, welcome to my English learning website." test-kokoro.mp3 --voice af_heart
```

确认当前目录存在 `test-kokoro.mp3` 后，可以删除测试文件：

```bash
rm test-kokoro.mp3
```

Windows PowerShell 删除测试文件：

```powershell
Remove-Item test-kokoro.mp3
```

## 先执行 Dry Run

不要直接批量生成，先执行：

```bash
npm run audio:dry-run
```

这个命令只分析课程数据并打印将要执行的 Kokoro 命令，不会生成 MP3。

正常情况下，会看到类似内容：

```text
kokorosay Hello, I am Anna. ... public/audio/standard/...-female.mp3 --voice af_heart
kokorosay Hello, Leo. ... public/audio/standard/...-male.mp3 --voice am_adam
```

如果 dry-run 报错，先不要运行批量生成，检查当前目录和 Python 环境。

## 生成音频

### 推荐：先生成标准版

```bash
python3 scripts/generate_audio.py --mode standard
```

Windows：

```bash
python scripts/generate_audio.py --mode standard
```

标准版生成完成后，检查以下目录：

```text
public/audio/standard/
public/audio/manifest.json
```

### 生成口语版

```bash
python3 scripts/generate_audio.py --mode natural
```

### 生成听力辨音版

```bash
python3 scripts/generate_audio.py --mode dictation
```

### 一次生成全部版本

```bash
python3 scripts/generate_audio.py --mode all
```

也可以使用 npm 命令：

```bash
npm run audio:generate
```

## 生成结果

生成完成后，目录结构类似：

```text
public/audio/
├── manifest.json
├── standard/
│   ├── a1-l1-u1-d1-l1-female.mp3
│   └── a1-l1-u1-d1-l2-male.mp3
├── natural/
│   └── ...
└── dictation/
    └── ...
```

`manifest.json` 是前端判断静态音频是否存在的依据，不能删除。

如果只生成了标准版，网站仍然可以运行。切换到没有生成的模式时，浏览器会回退到系统语音。

## 启动并验证

启动开发服务器：

```bash
npm run dev
```

浏览器打开终端显示的地址，然后按以下步骤验证：

1. 打开一个已经生成音频的课程单元。
2. 点击任意英文句子的 `Play`。
3. 检查浏览器开发者工具的 Network 面板。
4. 确认请求路径类似 `/audio/standard/...mp3`。
5. 点击“听全部”，确认多条音频可以连续播放。
6. 切换到未生成的模式，确认仍然可以通过浏览器语音播放。

构建验证：

```bash
npm run type-check
npm run lint
npm run build
```

## AI 执行规则

AI 在本地操作时必须遵守：

1. 不要修改 `src/data/` 中的课程内容。
2. 不要把 Kokoro 模型文件复制到网站目录。
3. 不要新增后端服务。
4. 不要删除 `public/audio/manifest.json`。
5. 生成失败时保留已经成功生成的文件，修复问题后继续执行。
6. 重新生成前不要删除整个 `public/audio/`，除非用户明确要求。
7. 先运行单句测试，再运行 dry-run，最后执行批量生成。
8. 生成完成后必须运行 `npm run type-check` 和 `npm run build`。

## 常见问题

### 找不到 Python

安装 Python 3.10 或更高版本，并重新打开终端。

### 找不到 kokorosay

尝试：

```bash
python3 -m pip install --upgrade kokorosay
```

Windows：

```bash
python -m pip install --upgrade kokorosay
```

然后重新打开终端。

### 第一次生成很慢

第一次运行需要下载 Kokoro 模型。模型下载完成后，后续生成会更快。

### 磁盘空间不足

先只生成标准版：

```bash
python3 scripts/generate_audio.py --mode standard
```

不要一次生成全部三种模式。

### 某个音频生成失败

记录失败的命令，单独重新运行该命令。如果只失败少量文件，不要删除整个音频目录。

### 部署后没有声音

检查：

1. `public/audio/` 是否被提交或上传。
2. `public/audio/manifest.json` 是否存在。
3. MP3 文件路径大小写是否一致。
4. 部署平台是否正确发布了静态资源。

## 最终交付标准

以下命令都成功，才算完成：

```bash
npm run audio:dry-run
npm run type-check
npm run lint
npm run build
```

如果已经实际生成音频，还需要确认：

```text
public/audio/manifest.json 存在
public/audio/standard/ 至少包含一个 MP3
浏览器可以播放一个静态 MP3
```
