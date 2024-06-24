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
    def __init__(self, debug_mode: bool = False, num_files: Optional[int] = None):
        self.debug_mode = debug_mode
        self.songs = self.get_songs()
        self.song_titles = list(self.songs.keys())
        self.unguessed_files = self.get_unguessed_files(num_files)
        self.current_file: Optional[str] = None
        self.total_questions = len(self.unguessed_files)
        self.correct_answers = 0

    def get_songs(self) -> Dict[str, List[str]]:
        songs = {}
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith(".mp3"):
                name_without_ext = os.path.splitext(filename)[0]
                words = name_without_ext.split('_')
                song_title = ' '.join(word.capitalize() for word in words[:-1])
                audio_path = os.path.join(AUDIO_DIR, filename)
                songs.setdefault(song_title, []).append(audio_path)
        return songs

    def get_unguessed_files(self, num_files: Optional[int] = None) -> List[str]:
        all_files = [file for files in self.songs.values() for file in files]
        if num_files is None:
            num_files = len(all_files) if not self.debug_mode else 5
        if num_files < 1 or num_files > len(all_files):
            raise ValueError(f"Invalid number of files: {num_files}. Must be between 1 and {len(all_files)}.")
        return random.sample(all_files, num_files)

    def play_file(self):
        print("\nPlaying audio...")
        playsound(self.current_file)

    def display_song_list(self):
        print("List of songs:")
        for i, song in enumerate(self.song_titles, 1):
            print(f"{i}. {song}")

    def display_progress(self):
        print(f"\nAsking {self.total_questions} questions: {self.correct_answers} answered correctly so far.\n")

    def get_user_input(self) -> str:
        while True:
            user_input = input("\nEnter your choice: ").lower()
            if user_input in VALID_ACTIONS or user_input.isdigit() and 1 <= int(user_input) <= len(self.song_titles):
                return user_input
            print("Invalid input. Please try again.")

    def clear_screen(self):
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux, macOS
            os.system('clear')

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
            if self.check_guess(int(user_input) - 1):
                self.correct_answers += 1
            else:
                time.sleep(2)  # Pause for 2 seconds after a wrong answer
        return True

    def play(self):
        self.clear_screen()
        while self.unguessed_files:
            self.display_song_list()
            self.display_progress()
            self.select_and_play_file()
            self.display_debug_info()
            if not self.handle_user_interaction():
                break
            if self.unguessed_files:
                self.clear_screen()
        self.display_game_over_message()

    def select_and_play_file(self):
        if not self.current_file:
            self.current_file = random.choice(self.unguessed_files)
        self.play_file()

    def handle_user_interaction(self) -> bool:
        while True:
            user_input = self.get_user_input()
            if user_input != 'r':
                return self.handle_guess(user_input)
            self.play_file()

    def display_debug_info(self):
        if self.debug_mode:
            correct_answer = next(title for title, paths in self.songs.items() if self.current_file in paths)
            print(f"\nDebug: Correct answer is {correct_answer}")

    def display_game_over_message(self):
        if not self.unguessed_files:
            print("\nCongratulations! You've guessed all the tunes correctly!")
        else:
            print("\nThanks for playing!")

    def show_answer(self):
        song_title = next(title for title, paths in self.songs.items() if self.current_file in paths)
        print(f"\nThe correct song is: {song_title}")
        time.sleep(2)
        self.current_file = random.choice(self.unguessed_files)

    def check_guess(self, guess_index: int) -> bool:
        guessed_title = self.song_titles[guess_index]
        if self.current_file in self.songs[guessed_title]:
            print(f"\nCorrect! The audio clip is from {guessed_title}.")
            time.sleep(2)
            self.unguessed_files.remove(self.current_file)
            self.current_file = random.choice(self.unguessed_files) if self.unguessed_files else None
            if self.unguessed_files:
                self.clear_screen()  # Clear the screen
            return True
        else:
            print(f"\nIncorrect. Your guess was: {guessed_title}")
            print("Try again.")
            return False


def main():
    debug_mode = False
    num_files = None

    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if arg == '-d':
            debug_mode = True
        elif arg.isdigit():
            num_files = int(arg)

    try:
        game = ShucksGame(debug_mode, num_files)
        game.play()
    except ValueError as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()