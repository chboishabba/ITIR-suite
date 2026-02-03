# ITIR-suite

Meta-repo that pins the moving pieces of the ITIR / SensibLaw stack as git submodules. Use this repo to pull the whole toolchain in one shot; build and run inside the individual submodules.

## Components (submodules)
- `SensibLaw/` – ingestion + operations console for span-anchored legal corpora (see that repo for build/run docs).
- `SL-reasoner/` – reasoning/IR spine that the SensibLaw UI and tooling consume.
- `tircorder-JOBBIE/` – investigative/interpretive tooling (ITIR/TIRC experiments).
- `WhisperX-WebUI/` – speech-to-text pipeline + UI (WhisperX wrapper).
- `reverse-engineered-chatgpt` – wrapper for programmatic access to chatGPT interface (note, issues with sending messages - testing stalled due to bot detection - chat account otherwise unaffected).

The definitive instructions for each live in the submodule’s own README; this file only tracks how to manage them together.

## Quickstart
```bash
git clone https://github.com/chboishabba/ITIR-suite.git
cd ITIR-suite
./setup.sh   # runs `git submodule update --init --recursive`
```

If you already have the repo, sync to the recorded commits with:

```bash
git submodule update --init --recursive
```

## Working with submodules
- To pull latest from all submodules (fast-forward to upstream):
  ```bash
  git submodule update --remote --recursive
  ```
- To commit/push submodule changes in bulk (use with care), `sync-all-submodules.sh` will run `git add/commit/push` inside each submodule and then commit the updated pointers in this meta-repo.
- When changing a submodule, commit inside the submodule first, then `git add <submodule>` in this repo to record the new pointer.

## Notes
- This repo carries no standalone build; everything interesting happens inside the submodules.
- Keep `setup.sh` up to date if new modules are added.


## Dev Note
Due to technical constraints, the below command is used for running a compatibility docker. We are hoping to eventually provide ITIR as a deployable container separate to this as well.
The compatibility docker is provided due to development being conducted on AMD RX580 (gfx803), requiring some compiled modules due to importing torch/ctranslate2 for speech-to-text in WhisperX-WebUI.
This is already quite fast on CPU, especially with whisperx, and when VAD chunking is performed by tircorder, however does result in degradation of desktop experience for the server/host.
Most newer consumer cards will not require this compatibility layer.


```
docker run -it \
              --name ITIR \
              --device=/dev/kfd --device=/dev/dri \
              --security-opt seccomp=unconfined \
              --group-add video \
              -v /usr/include/vulkan:/usr/include/vulkan:ro \
              -v /usr/include/spirv:/usr/include/spirv:ro \
              -v /usr/include/vk_video:/usr/include/vk_video:ro \
              -v /usr/include/glslang:/usr/include/glslang:ro \
              -v /usr/bin/glslangValidator:/usr/bin/glslangValidator:ro \
              -v "/home/c/Documents/code/ITIR-suite:/opt/ITIR-suite" \
              --entrypoint /bin/bash \
              dashi_ready_image
```
then ``` cd /opt/ITIR-suite (linked to host)```
and ```source /Whisper-WebUI/venv/bin/activate```
