# ComfyUI Load Text Batch From Dir

A text version of **Load Image Batch From Dir (Inspire)** from [ComfyUI-Inspire-Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack).
It reads the text files in a folder, in the order you choose, and loads as many as you ask for. Point it at a folder of prompts and step through them one per run.

Companion to [comfyui-load-audio-batch-from-dir](https://github.com/roychodraws87/comfyui-load-audio-batch-from-dir) and [comfyui-load-video-batch-from-dir](https://github.com/roychodraws87/comfyui-load-video-batch-from-dir).

## Install
Copy this folder into `ComfyUI/custom_nodes/` and restart ComfyUI. No extra packages are needed.
The node appears as **Load Text Batch From Dir** under `text`.

## Inputs
| Input | Default | Meaning |
|---|---|---|
| `directory` | | Folder to read |
| `text_load_cap` | 0 | Load at most this many files (0 = no limit) |
| `start_index` | 0 | Skip this many files first (-1 = the last file) |
| `load_always` | off | Re-run every time instead of only when the inputs or the folder change |
| `sort_method` | None | None, Alphabetical, Numerical (first number in the file name) or Datetime, ascending or descending |
| `separator` | `\n\n` | Put between files when more than one is loaded. `\n` is a line break, `\t` a tab |
| `strip` | on | Trim blank lines and spaces from the start and end of each file |

## Outputs
* `text` - the loaded file (txt, md, prompt, text, json, yaml, yml, csv)
* `count` - how many files were loaded

An image batch stacks frames, but there is no such thing as a batch of strings, so several files are joined one after another with `separator` between them.

Files are read as UTF-8, then UTF-8 with a BOM, then latin-1, so a file saved from any editor still loads.

**One prompt per run:** set `text_load_cap` to 1 and drive `start_index` with a counter (for example a primitive set to *increment*) to step through a folder, one file per queued run.

## Differences from the Inspire node
* Text files instead of images; no mask output; adds the separator and strip controls.
* Folders that happen to match a file extension are skipped (the original crashes on them).
* The change check looks at the input values and the files' modified times, not only the input names.

## Status
File selection, sorting, the encodings, the join, the separator and strip were tested on real files outside ComfyUI. It has not been run inside ComfyUI yet. Please open an issue with the error text if a file fails to load.

## Credits
Adapted from `LoadImagesFromDirBatch` in [ComfyUI-Inspire-Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack) by ltdrdata (GPL-3.0). Released under the same licence (GPL-3.0).
