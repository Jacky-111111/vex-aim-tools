#!/usr/bin/env python3

from pathlib import Path


input_dir = Path("sft_training/training_data/v3") # change to any folder with the training examples in .jsonl files
output_file = Path("sft_training/training_data/training_sft_v3.jsonl")

files = sorted(input_dir.glob("*.jsonl"), key=lambda path: int(path.stem))

with output_file.open("w", encoding="utf-8") as output:
    for file in files:
        output.write(file.read_text(encoding="utf-8").rstrip())
        output.write("\n")

print(f"Successfully combined {len(files)} files into {output_file}!")
