#!/usr/bin/env python3

import os
import time
from mutagen import File
import subprocess
import glob
from pathlib import Path


class MusicPlayer:
    def __init__(self):
        self.music_dir = "/home/user/music"  # Change this to your music directory
        self.music_library = {}
        self.current_song = None
        self.process = None
        self.is_playing = False
        # Supported audio formats
        self.supported_formats = ('.mp3', '.flac', '.wav', '.ogg')

    def build_library(self):
        print("Scanning music directory...")
        music_path = os.path.expanduser(self.music_dir)

        # Search for all supported filetypes
        files = []
        for fmt in self.supported_formats:
            files.extend(glob.glob(f"{music_path}/**/*{fmt}", recursive=True))

        for idx, song_path in enumerate(files):
            try:
                audio = File(song_path, easy=True)
                if audio is None:
                    continue

                # Handle different tag formats
                artist = audio.get('artist', ['Unknown'])[0] if 'artist' in audio else 'Unknown'
                title = audio.get('title', ['Unknown'])[0] if 'title' in audio else Path(song_path).stem

                self.music_library[idx] = {
                    'path': song_path,
                    'artist': artist,
                    'title': title
                }
            except Exception as e:
                # Skip files that can't be processed
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
        # Using ffplay with -nodisp to prevent video window and -autoexit to stop when done
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
        self.build_library()

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
