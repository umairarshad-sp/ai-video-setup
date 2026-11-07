#!/usr/bin/env bash
# One-time setup for a fresh session: Node tools (HyperFrames, GSAP, three.js),
# a Python env (Kokoro TTS, image tools, Freesound client) and the Kokoro voice model.
#
#   bash setup.sh
#
# Safe to re-run: it skips whatever is already in place.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Node packages (hyperframes, gsap, three)"
npm ci --no-audit --no-fund

echo "==> Python env (.venv)"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

echo "==> Kokoro voice model (models/)"
mkdir -p models
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
declare -A sums=(
  [kokoro-v1.0.onnx]=7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5
  [voices-v1.0.bin]=bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d
)
for f in "${!sums[@]}"; do
  if ! echo "${sums[$f]}  models/$f" | sha256sum -c --status 2>/dev/null; then
    echo "    downloading $f"
    curl -sSL -o "models/$f" "$base/$f"
    echo "${sums[$f]}  models/$f" | sha256sum -c --quiet
  fi
done

echo "==> Indic Parler-TTS env (.venv-parler) for the character voices"
if [[ ! -x .venv-parler/bin/python ]]; then
  python3 -m venv .venv-parler
fi
.venv-parler/bin/pip install -q --upgrade pip
.venv-parler/bin/pip install -q -r requirements-parler.txt
if [[ -n "${HF_TOKEN:-}" ]]; then
  # downloads ai4bharat/indic-parler-tts (~3.5 GB) into the Hugging Face cache once per session
  .venv-parler/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('ai4bharat/indic-parler-tts')" >/dev/null
else
  echo "    HF_TOKEN not set: Indic Parler-TTS voices will not work (see CLAUDE.md)"
fi

echo "==> Skills"
# The repo's .claude/skills/ load automatically when Claude Code opens this folder.
ls .claude/skills

mkdir -p build output work
echo
echo "Setup done. Try:  .venv/bin/python studio/build_episode.py episodes/001_part1.json"
