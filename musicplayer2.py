#!/usr/bin/env python3

import os
import subprocess
import glob
from pathlib import Path
from mutagen import File


class MusicPlayer:
    def __init__(self):
        self.music_library = {}
        self.current_song = None
        self.process = None
        self.is_playing = False
        self.supported_formats = ('.mp3', '.flac', '.wav', '.ogg')

    def browse_directory(self):
        current_dir = "/"  # Start at root directory
        while True:
            print(f"\nCurrent directory: {current_dir}")
            print("Directories and options:")
            print("-" * 50)

            # List directories
            dirs = [d for d in os.listdir(current_dir)
                    if os.path.isdir(os.path.join(current_dir, d))]
            dirs.sort()
            for i, d in enumerate(dirs):
                print(f"{i}: {d}")

            # Additional options
            print(f"p: Use parent directory ({os.path.dirname(current_dir)})")
            print("s: Select this directory")
            print("q: Quit")

            choice = input("> ").strip().lower()

            if choice.isdigit():
                idx = int(choice)
                if 0 <= idx < len(dirs):
                    current_dir = os.path.join(current_dir, dirs[idx])
                else:
                    print("Invalid directory number")

            elif choice == 'p':
                parent = os.path.dirname(current_dir)
                if parent != current_dir:  # Avoid infinite loop at root
                    current_dir = parent
                else:
                    print("Already at root")

            elif choice == 's':
                return current_dir

            elif choice == 'q':
                print("Goodbye!")
                exit(0)

            else:
                print("Invalid option")

    def build_library(self, music_dir):
        print("Scanning music directory...")
        files = []
        for fmt in self.supported_formats:
            files.extend(glob.glob(f"{music_dir}/**/*{fmt}", recursive=True))

        for idx, song_path in enumerate(files):
            try:
                audio = File(song_path, easy=True)
                if audio is None:
                    continue

                artist = audio.get('artist', ['Unknown'])[0] if 'artist' in audio else 'Unknown'
                title = audio.get('title', ['Unknown'])[0] if 'title' in audio else Path(song_path).stem

                self.music_library[idx] = {
                    'path': song_path,
                    'artist': artist,
                    'title': title
                }
            except Exception as e:
                print(f"Skipping {song_path}: {str(e)}")
                continue

        print(f"Found {len(self.music_library)} songs")

    def display_library(self):
        print("\nMusic Library:")
        print("-" * 50)
        for idx, song in self.music_library.items():
            print(f"{idx}: {song['artist']} - {song['title']}")
        print("-" * 50)

    def play_song(self, song_idx):
        if song_idx not in self.music_library:
            print("Invalid song selection")
            return

        if self.is_playing:
            self.stop_song()

        self.current_song = self.music_library[song_idx]
        print(f"\nPlaying: {self.current_song['artist']} - {self.current_song['title']}")
        self.process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', self.current_song['path']],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
        self.is_playing = True

    def stop_song(self):
        if self.process:
            self.process.terminate()
            self.is_playing = False
            self.process = None

    def run(self):
        music_dir = self.browse_directory()
        self.build_library(music_dir)

        while True:
            self.display_library()
            print("\nCommands:")
            print("p <number> - Play song")
            print("s - Stop current song")
            print("q - Quit")

            choice = input("> ").strip().lower()

            if choice.startswith('p '):
                try:
                    song_idx = int(choice.split()[1])
                    self.play_song(song_idx)
                except (ValueError, IndexError):
                    print("Invalid song number")

            elif choice == 's':
                self.stop_song()
                print("Stopped")

            elif choice == 'q':
                self.stop_song()
                print("Goodbye!")
                break

            else:
                print("Invalid command")


if __name__ == "__main__":
    player = MusicPlayer()
    try:
        player.run()
    except KeyboardInterrupt:
        player.stop_song()
        print("\nStopped by user")
