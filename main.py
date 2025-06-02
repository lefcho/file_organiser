import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class FileCategorizer:
    def __init__(self, ext_map):
        """
        ext_map: dict mapping extensions (e.g. 'txt') to folder names (e.g. 'TextFiles').
        """
        # Normalize keys: remove leading dot and use lower case
        self.ext_map = {k.lower().lstrip('.'): v for k, v in ext_map.items()}

    def categorize(self, directory):
        """
        Scan the top-level of 'directory' and group files by the ext_map.
        Returns a dict: {folder_name: [file1, file2, ...], ...}
        """
        result = {}
        directory_path = Path(directory)
        for item in directory_path.iterdir():
            if item.is_file():
                ext = item.suffix.lower().lstrip('.')
                if ext in self.ext_map:
                    folder = self.ext_map[ext]
                    result.setdefault(folder, []).append(item.name)
        return result


class FileOrganizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("File Organizer")
        self.selected_dir = None
        self.mapping_rows = []  # List of frames for mapping entries
        self._build_gui()

    def _build_gui(self):
        # Frame for folder selection
        frame_dir = tk.Frame(self.root)
        frame_dir.pack(padx=10, pady=5, fill='x')
        btn_browse = tk.Button(frame_dir, text="Select Folder", command=self.select_folder)
        btn_browse.pack(side='left')
        self.lbl_path = tk.Label(frame_dir, text="No folder selected", anchor='w')
        self.lbl_path.pack(side='left', padx=5)

        # Frame for mapping entries
        frame_map = tk.Frame(self.root, relief='groove', bd=1)
        frame_map.pack(padx=10, pady=5, fill='x')
        tk.Label(frame_map, text="Extension").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        tk.Label(frame_map, text="Target Folder").grid(row=0, column=1, padx=5, pady=2, sticky='w')
        self.map_frame = tk.Frame(frame_map)
        self.map_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')
        # Add initial mapping row
        self.add_mapping_row()

        btn_add = tk.Button(frame_map, text="Add Mapping", command=self.add_mapping_row)
        btn_add.grid(row=2, column=0, columnspan=2, pady=5)

        # Frame for action buttons
        frame_actions = tk.Frame(self.root)
        frame_actions.pack(padx=10, pady=5)
        btn_preview = tk.Button(frame_actions, text="Preview", command=self.preview)
        btn_preview.pack(side='left', padx=5)
        btn_done = tk.Button(frame_actions, text="Done", command=self.done)
        btn_done.pack(side='left', padx=5)

        # Frame for treeview result
        frame_tree = tk.Frame(self.root)
        frame_tree.pack(padx=10, pady=5, fill='both', expand=True)
        self.tree = ttk.Treeview(frame_tree)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

    def select_folder(self):
        """Open a directory chooser and display the selected path."""
        path = filedialog.askdirectory()
        if path:
            self.selected_dir = path
            self.lbl_path.config(text=path)

    def add_mapping_row(self):
        """Add a new row of entries for extension-to-folder mapping."""
        row_frame = tk.Frame(self.map_frame)
        ext_entry = tk.Entry(row_frame, width=10)
        ext_entry.pack(side='left', padx=5, pady=2)
        folder_entry = tk.Entry(row_frame, width=20)
        folder_entry.pack(side='left', padx=5, pady=2)
        btn_remove = tk.Button(row_frame, text="Remove", command=lambda: self.remove_mapping_row(row_frame))
        btn_remove.pack(side='left', padx=5)
        row_frame.pack(fill='x')
        self.mapping_rows.append((row_frame, ext_entry, folder_entry))

    def remove_mapping_row(self, row_frame):
        """Remove a mapping row."""
        # Find and destroy the row frame
        for i, (frame, ext, folder) in enumerate(self.mapping_rows):
            if frame == row_frame:
                frame.destroy()
                self.mapping_rows.pop(i)
                break

    def get_mappings(self):
        """Retrieve mappings from the GUI entries as a dict {ext: folder}."""
        mappings = {}
        for _, ext_entry, folder_entry in self.mapping_rows:
            ext = ext_entry.get().strip().lower().lstrip('.')
            folder = folder_entry.get().strip()
            if ext and folder:
                mappings[ext] = folder
        return mappings

    def preview(self):
        """Compute and display the file organization in the treeview."""
        if not self.selected_dir:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        mappings = self.get_mappings()
        if not mappings:
            messagebox.showerror("Error", "Please add at least one mapping rule.")
            return
        categorizer = FileCategorizer(mappings)
        result = categorizer.categorize(self.selected_dir)
        # Clear previous treeview items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insert new results
        for folder, files in result.items():
            parent_id = self.tree.insert("", tk.END, text=folder)
            for filename in files:
                self.tree.insert(parent_id, tk.END, text=filename)

    def done(self):
        """Create folders and move the files as per the mappings."""
        if not self.selected_dir:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        mappings = self.get_mappings()
        if not mappings:
            messagebox.showerror("Error", "No mapping rules to apply.")
            return
        categorizer = FileCategorizer(mappings)
        result = categorizer.categorize(self.selected_dir)
        # Perform the file moves
        for folder, files in result.items():
            target_dir = Path(self.selected_dir) / folder
            target_dir.mkdir(exist_ok=True)
            for filename in files:
                src = Path(self.selected_dir) / filename
                dst = target_dir / filename
                try:
                    src.rename(dst)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to move {filename}: {e}")
        messagebox.showinfo("Done", "Files have been organized.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FileOrganizerGUI()
    app.run()
