#!/usr/bin/env python3

import os
import subprocess
import glob
from pathlib import Path
from mutagen import File
import tkinter as tk
from tkinter import ttk, messagebox


def run_gui():
    """Function to run the GUI."""

    class MusicPlayer:
        def __init__(self):
            self.music_library = {}
            self.current_song = None
            self.process = None
            self.is_playing = False
            self.supported_formats = ('.mp3', '.flac', '.wav', '.ogg')
            self.root = tk.Tk()
            self.root.title("Purple Future Music Player")
            self.root.geometry("600x400")
            self.setup_theme()
            self.setup_gui()

        def setup_theme(self):
            style = ttk.Style()
            style.theme_use('default')

            dark_purple = "#2a1a4a"
            light_purple = "#6b5b95"
            neon_purple = "#9b59b6"
            text_color = "#e8e8e8"

            self.root.configure(bg=dark_purple)
            style.configure("TFrame", background=dark_purple)
            style.configure("TButton",
                            background=light_purple,
                            foreground=text_color,
                            borderwidth=1,
                            font=("Arial", 10, "bold"))
            style.map("TButton",
                      background=[("active", neon_purple)],
                      foreground=[("active", text_color)])
            style.configure("TLabel",
                            background=dark_purple,
                            foreground=text_color,
                            font=("Arial", 10))

            self.root.option_add("*Listbox.background", dark_purple)
            self.root.option_add("*Listbox.foreground", text_color)
            self.root.option_add("*Listbox.selectBackground", neon_purple)
            self.root.option_add("*Listbox.selectForeground", text_color)
            self.root.option_add("*Listbox.font", ("Arial", 10))

        def browse_directory(self):
            browse_window = tk.Toplevel(self.root)
            browse_window.title("Select Music Directory")
            browse_window.geometry("400x300")
            browse_window.configure(bg="#2a1a4a")

            current_dir = tk.StringVar(value="/")
            dir_listbox = tk.Listbox(browse_window, height=15)
            dir_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            def update_dir_list():
                dir_listbox.delete(0, tk.END)
                dirs = [d for d in os.listdir(current_dir.get())
                        if os.path.isdir(os.path.join(current_dir.get(), d))]
                dirs.sort()
                for d in dirs:
                    dir_listbox.insert(tk.END, d)
                self.root.update()

            def go_to_dir(event):
                selection = dir_listbox.curselection()
                if selection:
                    new_dir = os.path.join(current_dir.get(), dir_listbox.get(selection[0]))
                    current_dir.set(new_dir)
                    update_dir_list()

            def go_parent():
                parent = os.path.dirname(current_dir.get())
                if parent != current_dir.get():
                    current_dir.set(parent)
                    update_dir_list()

            def select_dir():
                self.music_dir = current_dir.get()
                browse_window.destroy()
                self.build_library()

            ttk.Label(browse_window, textvariable=current_dir).pack(pady=5)
            dir_listbox.bind("<Double-1>", go_to_dir)
            update_dir_list()

            ttk.Button(browse_window, text="Parent", command=go_parent).pack(side=tk.LEFT, padx=5, pady=5)
            ttk.Button(browse_window, text="Select", command=select_dir).pack(side=tk.RIGHT, padx=5, pady=5)

        def build_library(self):
            self.music_library.clear()
            self.song_listbox.delete(0, tk.END)
            files = []
            for fmt in self.supported_formats:
                files.extend(glob.glob(f"{self.music_dir}/**/*{fmt}", recursive=True))

            for idx, song_path in enumerate(files):
                try:
                    audio = File(song_path, easy=True)
                    if audio is None:
                        continue
                    artist = audio.get('artist', ['Unknown'])[0] if 'artist' in audio else 'Unknown'
                    title = audio.get('title', ['Unknown'])[0] if 'title' in audio else Path(song_path).stem
                    self.music_library[idx] = {'path': song_path, 'artist': artist, 'title': title}
                    self.song_listbox.insert(tk.END, f"{artist} - {title}")
                except Exception as e:
                    print(f"Skipping {song_path}: {str(e)}")
            self.status_label.config(text=f"Found {len(self.music_library)} songs")

        def play_song(self, song_idx=None):
            if song_idx is None:
                selection = self.song_listbox.curselection()
                if not selection:
                    return
                song_idx = selection[0]

            if song_idx not in self.music_library:
                messagebox.showerror("Error", "Invalid song selection")
                return

            if self.is_playing:
                self.stop_song()

            self.current_song = self.music_library[song_idx]
            self.status_label.config(text=f"Playing: {self.current_song['artist']} - {self.current_song['title']}")
            self.process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', self.current_song['path']],
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.is_playing = True

        def stop_song(self):
            if self.process:
                self.process.terminate()
                self.is_playing = False
                self.process = None
                self.status_label.config(text="Stopped")

        def setup_gui(self):
            frame = ttk.Frame(self.root)
            frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
            self.song_listbox = tk.Listbox(frame, height=15, yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.song_listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.song_listbox.pack(fill=tk.BOTH, expand=True)
            self.song_listbox.bind("<Double-1>", lambda e: self.play_song())

            control_frame = ttk.Frame(self.root)
            control_frame.pack(fill=tk.X, padx=5, pady=5)
            ttk.Button(control_frame, text="Play", command=self.play_song).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Stop", command=self.stop_song).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT, padx=5)

            self.status_label = ttk.Label(self.root, text="Select a directory to begin")
            self.status_label.pack(fill=tk.X, padx=5, pady=5)

        def run(self):
            self.browse_directory()
            self.root.mainloop()

        def on_closing(self):
            self.stop_song()
            self.root.destroy()

    player = MusicPlayer()
    player.root.protocol("WM_DELETE_WINDOW", player.on_closing)
    player.run()


if __name__ == "__main__":
    # Fork the process to detach the GUI
    pid = os.fork()
    if pid > 0:
        # Parent process exits immediately, freeing the terminal
        exit(0)
    else:
        # Child process runs the GUI
        # Detach from terminal
        os.setsid()  # Create new session
        run_gui()