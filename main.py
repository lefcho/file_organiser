import os
from pathlib import Path

class FileCategorizer:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.mapping = {}  # e.g. {".jpg": "Images", ".pdf": "Documents"}

    def set_rules(self, mapping_dict):
        self.mapping = mapping_dict

    def compute_preview(self):
        preview = {}
        for entry in os.scandir(self.folder_path):
            if entry.is_dir():
                continue
            ext = Path(entry.name).suffix.lower()
            target = self.mapping.get(ext, "Unsorted")
            preview.setdefault(target, []).append(entry.name)
        return preview

    def apply_changes(self):
        for entry in os.scandir(self.folder_path):
            if entry.is_dir():
                continue
            file_path = Path(entry.path)
            ext = file_path.suffix.lower()
            if ext in self.mapping:
                dest_folder = self.folder_path / self.mapping[ext]
                dest_folder.mkdir(exist_ok=True)
                file_path.rename(dest_folder / file_path.name)
