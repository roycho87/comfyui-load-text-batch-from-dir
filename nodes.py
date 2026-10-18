"""Load Text Batch From Dir  --  text version of "Load Image Batch From Dir (Inspire)".

Same inputs and behaviour as the Inspire node, for text files:
  directory       folder to read
  text_load_cap   load at most this many files (0 = no limit)           [image_load_cap]
  start_index     skip this many files first (-1 = the last file)       [start_index]
  load_always     re-run every time instead of only when inputs change  [load_always]
  sort_method     None / Alphabetical / Numerical / Datetime, ASC or DESC

Outputs: STRING and INT (number of files loaded), like IMAGE / MASK / INT.
An image batch stacks frames, but there is no such thing as a batch of strings, so the files are joined one
after another into a single STRING with `separator` between them (a blank line by default).

The usual way to use it is one prompt per run: text_load_cap 1 with start_index driven by an incrementing
counter, which steps through a folder of prompts a file at a time.

Adapted from ComfyUI-Inspire-Pack (image_util.py) by ltdrdata, GPL-3.0.
Drop this folder into ComfyUI/custom_nodes/ and restart ComfyUI.
"""
import os
import re

TEXT_EXTENSIONS = (".txt", ".md", ".prompt", ".text", ".json", ".yaml", ".yml", ".csv")

SORT_METHODS = [
    "None",
    "Alphabetical (ASC)",
    "Alphabetical (DESC)",
    "Numerical (ASC)",
    "Numerical (DESC)",
    "Datetime (ASC)",
    "Datetime (DESC)",
]


def _first_number(s):
    m = re.search(r"\d+", s)
    return int(m.group()) if m else float("inf")


def _sort_by(items, base_path=".", method=None):
    def full(x):
        return os.path.join(base_path, x)

    def stamp(path):
        try:
            return os.path.getmtime(path)
        except OSError:
            return float("-inf")

    if method == "Alphabetical (ASC)":
        return sorted(items)
    if method == "Alphabetical (DESC)":
        return sorted(items, reverse=True)
    if method == "Numerical (ASC)":
        return sorted(items, key=lambda x: _first_number(os.path.splitext(x)[0]))
    if method == "Numerical (DESC)":
        return sorted(items, key=lambda x: _first_number(os.path.splitext(x)[0]), reverse=True)
    if method == "Datetime (ASC)":
        return sorted(items, key=lambda x: stamp(full(x)))
    if method == "Datetime (DESC)":
        return sorted(items, key=lambda x: stamp(full(x)), reverse=True)
    return items


def _read_text(path):
    """-> the file's text. utf-8 first, then utf-8 with a BOM, then latin-1 so nothing fails to load."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as fh:
                return fh.read().lstrip("﻿")
        except UnicodeDecodeError:
            continue
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", "replace")


class LoadTextBatchFromDir:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
            },
            "optional": {
                "text_load_cap": ("INT", {"default": 0, "min": 0, "step": 1}),
                "start_index": ("INT", {"default": 0, "min": -1, "max": 0xffffffffffffffff, "step": 1}),
                "load_always": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
                "sort_method": (SORT_METHODS,),
                "separator": ("STRING", {"default": "\\n\\n", "multiline": False,
                                         "tooltip": "Put between files when more than one is loaded. \\n is a line break."}),
                "strip": ("BOOLEAN", {"default": True, "label_on": "enabled", "label_off": "disabled",
                                      "tooltip": "Trim blank lines and spaces from the start and end of each file."}),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "count")
    FUNCTION = "load_text"
    CATEGORY = "text"

    @classmethod
    def IS_CHANGED(cls, directory="", text_load_cap=0, start_index=0, load_always=False, sort_method=None,
                   separator="\\n\\n", strip=True, **kwargs):
        if load_always:
            return float("NaN")
        stamp = []
        try:
            for f in sorted(os.listdir(directory)):
                p = os.path.join(directory, f)
                if f.lower().endswith(TEXT_EXTENSIONS):
                    stamp.append((f, os.path.getmtime(p)))
        except OSError:
            pass
        return hash((directory, text_load_cap, start_index, sort_method, separator, strip, tuple(stamp)))

    def load_text(self, directory: str, text_load_cap: int = 0, start_index: int = 0, load_always=False,
                  sort_method=None, separator="\\n\\n", strip=True):
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory '{directory}' cannot be found.")
        files = os.listdir(directory)
        if len(files) == 0:
            raise FileNotFoundError(f"No files in directory '{directory}'.")

        files = [f for f in files if f.lower().endswith(TEXT_EXTENSIONS) and os.path.isfile(os.path.join(directory, f))]
        files = _sort_by(files, directory, sort_method)
        files = [os.path.join(directory, f) for f in files]
        files = files[start_index:]
        if text_load_cap > 0:
            files = files[:text_load_cap]
        if len(files) == 0:
            raise FileNotFoundError(f"No text files to load in '{directory}' (check start_index and the file types).")

        parts = []
        for path in files:
            text = _read_text(path)
            parts.append(text.strip() if strip else text)

        joiner = str(separator).replace("\\n", "\n").replace("\\t", "\t")
        out = parts[0] if len(parts) == 1 else joiner.join(parts)
        print(f"[Load Text Batch From Dir] {', '.join(os.path.basename(f) for f in files)}: {len(out)} characters")
        return (out, len(parts))


NODE_CLASS_MAPPINGS = {"LoadTextBatchFromDir": LoadTextBatchFromDir}
NODE_DISPLAY_NAME_MAPPINGS = {"LoadTextBatchFromDir": "Load Text Batch From Dir"}
