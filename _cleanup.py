from pathlib import Path
import re

p = Path(".")

bad_files = [
    'utils.py',
    'mannequin.json',
    'chunk_slicer.py',
    'custom_operator.py',
    'keymap_settings.py',
]

for folder in p.iterdir():
    if folder.is_dir() and "git" not in folder.name:
        for file in folder.iterdir():
            if file.name not in bad_files:
                with open(file.resolve(), "r") as f:
                    contents = f.readlines()
                for i, line in enumerate(contents[:]):
                    if re.search('def register\(\)\:', line):
                        contents.insert(i - 1, "addon_keymaps = []")
                with open(file.resolve(), "w") as f:
                    new_contents = "".join(contents)
                    f.write(new_contents)
