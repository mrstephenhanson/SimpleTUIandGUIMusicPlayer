#!/usr/bin/env python3

print("Before imports...")
import os
import subprocess
import glob
from pathlib import Path
from mutagen import File
import base64
import sys
print("Basic imports done...")
from PIL import Image
import io
print("Pillow imported...")

print("Starting script...")

class MusicPlayer:
    def __init__(self):
        print("Initializing MusicPlayer...")
        self.music_dir = "~/Music"
        self.music_library = {}
        self.current_song = None
        self.process = None
        self.is_playing = False
        self.supported_formats = ('.mp3', '.flac', '.wav', '.ogg')

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
                    'title': title,
                    'audio_obj': audio
                }
            except Exception as e:
                print(f"Skipping {song_path}: {str(e)}")
        print(f"Found {len(self.music_library)} songs")

    def display_library(self):
        print("\nMusic Library:")
        print("-" * 50)
        for idx, song in self.music_library.items():
            print(f"{idx}: {song['artist']} - {song['title']}")
        print("-" * 50)

    def resize_and_save_artwork(self, artwork, song_path):
        print("Resizing artwork...")
        max_size = 1_000_000  # 1MB
        song_dir = os.path.dirname(song_path)
        resized_path = os.path.join(song_dir, "cover_resized.jpg")

        if os.path.exists(resized_path):
            with open(resized_path, 'rb') as f:
                print("Using existing resized artwork")
                return f.read()

        img = Image.open(io.BytesIO(artwork))
        quality = 85
        scale_factor = 1.0

        while True:
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=quality)
            resized_data = output.getvalue()
            if len(resized_data) <= max_size or quality <= 10:
                break
            scale_factor *= 0.8
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            quality -= 10
            output.close()

        with open(resized_path, 'wb') as f:
            f.write(resized_data)
        print(f"Saved resized artwork to {resized_path} ({len(resized_data) // 1024}KB)")
        return resized_data

    def display_artwork(self, song):
        print("Skipping artwork display for now...")
        # Commented out entirely to avoid crashes
        # audio = song['audio_obj']
        # artwork = None
        
        # try:
        #     if hasattr(audio, 'pictures') and audio.pictures:
        #         artwork = audio.pictures[0].data
        #         print("Found FLAC artwork")
        #     elif 'APIC:' in audio:
        #         artwork = audio['APIC:'].data
        #         print("Found MP3 artwork")
            
        #     if artwork:
        #         print(f"Original artwork size: {len(artwork) // 1024}KB")
        #         if len(artwork) > 1_000_000:
        #             artwork = self.resize_and_save_artwork(artwork, song['path'])
        #         else:
        #             print("Artwork small enough, using original")
                
        #         print("Encoding artwork...")
        #         encoded = base64.b64encode(artwork).decode('ascii')
        #         print("Sending to Kitty...")
        #         sys.stdout.write("\033[2K")
        #         sys.stdout.write(f"\033_Gf=100,s=32,a=T;{encoded}\033\\")
        #         sys.stdout.flush()
        #         print("Artwork sent")
        #     else:
        #         print("(No artwork available)")
        # except Exception as e:
        #     print(f"Failed to display artwork: {e}")

    def play_song(self, song_idx):
        print("Playing song...")
        if song_idx not in self.music_library:
            print("Invalid song selection")
            return

        if self.is_playing:
            self.stop_song()

        self.current_song = self.music_library[song_idx]
        print(f"\nPlaying: {self.current_song['artist']} - {self.current_song['title']}")
        self.display_artwork(self.current_song)
        print("Starting ffplay...")
        self.process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', self.current_song['path']],
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
        self.is_playing = True
        print("ffplay started")

    def stop_song(self):
        print("Stopping song...")
        if self.process:
            self.process.terminate()
            self.is_playing = False
            self.process = None
            print("\033[2KStopped")

    def browse_directory(self):
        print("Starting directory browser...")
        current_dir = "/"
        while True:
            print(f"\nCurrent directory: {current_dir}")
            print("Directories and options:")
            print("-" * 50)
            
            dirs = [d for d in os.listdir(current_dir) 
                   if os.path.isdir(os.path.join(current_dir, d))]
            dirs.sort()
            for i, d in enumerate(dirs):
                print(f"{i}: {d}")
            
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
                if parent != current_dir:
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

    def run(self):
        print("Running music player...")
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
    print("Entering main...")
    player = MusicPlayer()
    try:
        player.run()
    except KeyboardInterrupt:
        player.stop_song()
        print("\nStopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")