"""
Shucks: A musical guessing game.

This program presents users with audio fragments and challenges them to
match each fragment with its corresponding song title. It's designed to
help users learn to associate audio clips with song names.

The program can be run in normal or debug mode, and allows for various
user interactions such as skipping, replaying, or requesting the answer
for each audio clip.
"""

import os
import random
import sys
import time
from typing import Dict, List, Optional

import pygame
import threading


DEBUG = False
AUDIO_DIR = "audio_files"
VALID_ACTIONS = {'s', 'S', 'a', 'A', 'r', 'R', 'q', 'Q'}
SLEEP_SECS = 1.5


class ShucksGame:
    """
    Represents the main game logic for Shucks.

    This class handles the game setup, audio playback, user interactions,
    and game progression.

    Attributes:
        debug_mode (bool): Whether the game is in debug mode.
        songs (Dict[str, List[str]]): Dictionary mapping song titles to audio file paths.
        song_titles (List[str]): Sorted list of song titles.
        unguessed_files (List[str]): List of audio files yet to be guessed.
        current_file (Optional[str]): Currently playing audio file.
        total_questions (int): Total number of questions to be asked.
        correct_answers (int): Number of correct answers given.
    """

    def __init__(self, debug_mode: bool = False, num_files: Optional[int] = None):
        """
        Initialize the ShucksGame.

        Args:
            debug_mode (bool): Whether to run the game in debug mode.
            num_files (Optional[int]): Number of files to use in the game.
        """
        self.debug_mode = debug_mode
        self.songs = self.get_songs()
        self.song_titles = sorted(list(self.songs.keys()))
        self.unguessed_files = self.get_unguessed_files(num_files)
        self.current_file: Optional[str] = None
        self.total_questions = len(self.unguessed_files)
        self.correct_answers = 0

        pygame.mixer.init()
        self.audio_thread = None
        self.stop_audio = False

    def __del__(self):
        """Clean up pygame mixer when the object is destroyed."""
        pygame.mixer.quit()

    @staticmethod
    def get_songs() -> Dict[str, List[str]]:
        """
        Get a dictionary of song titles and their corresponding audio file paths.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are song titles and values are lists of file paths.
        """
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
        """
        Get a list of unguessed audio files.

        Args:
            num_files (Optional[int]): Number of files to select. If None, uses all files in normal mode or 5 in debug mode.

        Returns:
            List[str]: A list of file paths for unguessed audio files.

        Raises:
            ValueError: If the specified number of files is invalid.
        """
        all_files = [file for files in self.songs.values() for file in files]
        if num_files is None:
            num_files = len(all_files) if not self.debug_mode else 5
        if num_files < 1 or num_files > len(all_files):
            raise ValueError(f"Invalid number of files: {num_files}. Must be between 1 and {len(all_files)}.")
        return random.sample(all_files, num_files)

    def play_file(self):
        """Play the current audio file in a separate thread."""
        print("\nPlaying audio...")
        self.play_audio_in_thread()

    def display_song_list(self):
        """Display the numbered list of song titles."""
        print("List of songs:")
        for i, song in enumerate(self.song_titles, 1):
            print(f"{i}.{' ' * (i <= 9)} {song}")

    def play_audio_in_thread(self):
        """Start playing the current audio file in a separate thread."""
        if self.current_file:
            self.stop_audio = False
            sound = pygame.mixer.Sound(self.current_file)
            self.audio_thread = threading.Thread(target=self.play_audio, args=(sound,))
            self.audio_thread.start()

    def play_audio(self, sound):
        """
        Play the audio and handle stopping.

        Args:
            sound: The pygame Sound object to play.
        """
        sound.play()
        while pygame.mixer.get_busy() and not self.stop_audio:
            time.sleep(0.1)
        sound.stop()

    def display_progress(self):
        """Display the current game progress."""
        print(f"\nAsking {self.total_questions} questions: {self.correct_answers} answered correctly so far.\n")

    def get_user_input(self) -> str:
        """
        Get and validate user input.

        Returns:
            str: The validated user input.
        """
        while True:
            user_input = input("\nEnter your choice: ").lower()
            if user_input in VALID_ACTIONS or user_input.isdigit() and 1 <= int(user_input) <= len(self.song_titles):
                return user_input
            print("Invalid input. Please try again.")

    @staticmethod
    def clear_screen():
        """Clear the console screen."""
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux, macOS
            os.system('clear')

    def handle_guess(self, user_input: str) -> bool:
        """
        Handle the user's guess or action.

        Args:
            user_input (str): The user's input.

        Returns:
            bool: True if the game should continue, False if it should end.
        """
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
                time.sleep(SLEEP_SECS)  # Pause for 2 seconds after a wrong answer
        return True

    def play(self):
        """Main game loop."""
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
        """Select a new file if necessary and play it."""
        if not self.current_file:
            self.current_file = random.choice(self.unguessed_files)
        self.play_file()

    def handle_user_interaction(self) -> bool:
        """
        Handle user interaction for the current audio file.

        Returns:
            bool: True if the game should continue, False if it should end.
        """
        user_input = self.get_user_input()
        if user_input == 'r':
            self.stop_audio = True
            if self.audio_thread:
                self.audio_thread.join()
            self.play_file()
            return True
        else:
            self.stop_audio = True
            if self.audio_thread:
                self.audio_thread.join()
            return self.handle_guess(user_input)

    def display_debug_info(self):
        """Display debug information if in debug mode."""
        if self.debug_mode:
            correct_answer = next(title for title, paths in self.songs.items() if self.current_file in paths)
            print(f"\nDebug: Correct answer is {correct_answer}")

    def display_game_over_message(self):
        """Display the game over message."""
        if not self.unguessed_files:
            print("\nCongratulations! You've guessed all the tunes correctly!")
        else:
            print("\nThanks for playing!")

    def show_answer(self):
        """Show the correct answer for the current audio file."""
        song_title = next(title for title, paths in self.songs.items() if self.current_file in paths)
        print(f"\nThe correct song is: {song_title}")
        time.sleep(SLEEP_SECS)
        self.current_file = random.choice(self.unguessed_files)

    def check_guess(self, guess_index: int) -> bool:
        """
        Check if the user's guess is correct.

        Args:
            guess_index (int): The index of the guessed song in the song_titles list.

        Returns:
            bool: True if the guess is correct, False otherwise.
        """
        guessed_title = self.song_titles[guess_index]
        if self.current_file in self.songs[guessed_title]:
            print(f"\nCorrect! The audio clip is from {guessed_title}.")
            time.sleep(SLEEP_SECS)
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
    """
    Main function to run the Shucks game.

    Parses command-line arguments and initializes the game.
    """
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