from playsound import playsound
import os
import random
import time
import sys
from typing import Dict, List, Optional

DEBUG = False
AUDIO_DIR = "audio_files"
VALID_ACTIONS = {'s', 'a', 'r', 'q'}


class ShucksGame:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.songs = self.get_songs()
        self.song_titles = list(self.songs.keys())
        self.unguessed_files = self.get_unguessed_files()
        self.current_file: Optional[str] = None

    def get_songs(self) -> Dict[str, List[str]]:
        songs = {}
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith(".mp3"):
                name_without_ext = os.path.splitext(filename)[0]
                words = name_without_ext.split('_')
                song_title = ' '.join(word.capitalize() for word in words[:-1])
                audio_path = os.path.join(AUDIO_DIR, filename)
                songs.setdefault(song_title, []).append(audio_path)

        if self.debug_mode:
            return {title: paths[:1] for title, paths in list(songs.items())[:5]}
        return songs

    def get_unguessed_files(self) -> List[str]:
        return [file for files in self.songs.values() for file in files]

    def play_file(self):
        print("\nPlaying audio...")
        playsound(self.current_file)

    def display_song_list(self):
        print("List of songs:")
        for i, song in enumerate(self.song_titles, 1):
            print(f"{i}. {song}")

    def get_user_input(self) -> str:
        while True:
            user_input = input("\nEnter your choice: ").lower()
            if user_input in VALID_ACTIONS or user_input.isdigit() and 1 <= int(user_input) <= len(self.song_titles):
                return user_input
            print("Invalid input. Please try again.")

    def handle_guess(self, user_input: str) -> bool:
        if user_input == 'q':
            return False
        elif user_input == 's':
            self.current_file = random.choice(self.unguessed_files)
        elif user_input == 'a':
            self.show_answer()
        elif user_input == 'r':
            return True  # Just continue the loop, don't change the current file
        else:
            self.check_guess(int(user_input) - 1)
        return True

    def play(self):
        self.display_song_list()
        while self.unguessed_files:
            if not self.current_file:
                self.current_file = random.choice(self.unguessed_files)

            if self.debug_mode:
                correct_answer = next(title for title, paths in self.songs.items() if self.current_file in paths)
                print(f"Debug: Correct answer is {correct_answer}")

            self.play_file()  # Play the audio file

            while True:  # Inner loop for handling repeats
                user_input = self.get_user_input()
                if user_input != 'r':  # If not repeating, break the inner loop
                    if not self.handle_guess(user_input):
                        return  # Exit the game if user quits
                    break  # Break the inner loop to potentially play a new file
                self.play_file()  # If repeating, play the file again

        if not self.unguessed_files:
            print("\nCongratulations! You've guessed all the tunes correctly!")
        else:
            print("\nThanks for playing!")

    def show_answer(self):
        song_title = next(title for title, paths in self.songs.items() if self.current_file in paths)
        print(f"\nThe correct song is: {song_title}")
        time.sleep(2)
        self.current_file = random.choice(self.unguessed_files)

    def check_guess(self, guess_index: int):
        guessed_title = self.song_titles[guess_index]
        if self.current_file in self.songs[guessed_title]:
            print(f"\nCorrect! The audio clip is from {guessed_title}.")
            time.sleep(2)
            self.unguessed_files.remove(self.current_file)
            self.current_file = random.choice(self.unguessed_files) if self.unguessed_files else None
        else:
            print(f"\nIncorrect. Your guess was: {guessed_title}")
            print("Try again.")


def main():
    debug_mode = DEBUG or "-d" in sys.argv
    game = ShucksGame(debug_mode)
    game.play()


if __name__ == "__main__":
    main()