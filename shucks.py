"""
Shucks: A musical guessing game.

This program presents users with audio fragments and challenges them to
match each fragment with its corresponding song title. It's designed to
help users learn to associate audio clips with song names.

The program can be run in normal or debug mode, and allows for various
user interactions such as skipping, replaying, or requesting the answer
for each audio clip.
"""
from abc import ABC, abstractmethod
import os
import random
import sys
import termios
import time
import tty
from typing import Dict, List, Optional

import pygame
import threading


DEBUG = False
AUDIO_DIR = "audio_files"
VALID_ACTIONS = {'s', 'S', 'a', 'A', 'r', 'R', 'q', 'Q'}
SLEEP_SECS = 1.5


class ShucksGame(ABC):
    """
    Abstract base class representing the main game logic for Shucks.

    This class handles the game setup, audio playback, and game progression.
    User input methods are declared as abstract and should be implemented by subclasses.

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

    @abstractmethod
    def get_user_input(self) -> str:
        """
        Get and validate user input.

        Returns:
            str: The validated user input.
        """
        pass

    @staticmethod
    def clear_screen():
        """Clear the console screen."""
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux, macOS
            os.system('clear')

    @abstractmethod
    def handle_guess(self, user_input: str) -> bool:
        """
        Handle the user's guess or action.

        Args:
            user_input (str): The user's input.

        Returns:
            bool: True if the game should continue, False if it should end.
        """
        pass

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

    @abstractmethod
    def handle_user_interaction(self) -> bool:
        """
        Handle user interaction for the current audio file.

        Returns:
            bool: True if the game should continue, False if it should end.
        """
        pass

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

    @abstractmethod
    def show_answer(self):
        """Show the correct answer for the current audio file."""
        pass

    @abstractmethod
    def check_guess(self, guess_index: int) -> bool:
        """
        Check if the user's guess is correct.

        Args:
            guess_index (int): The index of the guessed song in the song_titles list.

        Returns:
            bool: True if the guess is correct, False otherwise.
        """
        pass


class NormalGameInput(ShucksGame):
    """
    Concrete implementation of ShucksGame with normal user input handling.
    """

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


class InteractiveGameInput(ShucksGame):
    """
    Interactive implementation of ShucksGame.
    This class provides an interactive user input handling where:
    - Alphabetic input and spaces are accepted
    - Letters are processed as soon as they are typed
    - The screen is updated after each letter, showing matching song titles
    - Audio plays once and stops
    - Space character replays the audio clip
    - Integer input is treated as invalid and discarded
    - Backspace on empty input has no effect
    """

    def __init__(self, debug_mode: bool = False, num_files: Optional[int] = None):
        """
        Initialize the InteractiveGameInput.

        Args:
            debug_mode (bool): Whether to run the game in debug mode.
            num_files (Optional[int]): Number of files to use in the game.
        """
        super().__init__(debug_mode, num_files)
        self.current_input = ""
        pygame.mixer.init()
        self.current_file = None
        self.audio_thread = None
        self.stop_audio = threading.Event()
        self.total_questions = len(self.songs)

    def __del__(self):
        """Clean up pygame mixer and audio thread when the object is destroyed."""
        self.stop_audio.set()
        if self.audio_thread:
            self.audio_thread.join()
        pygame.mixer.quit()

    def play(self):
        """
        Main game loop for interactive mode.
        Overrides the play method from ShucksGame.
        """
        self.clear_screen()
        while self.unguessed_files:
            self.select_new_file()
            self.display_game_state()
            self.play_file()

            while True:
                char = self.get_char()
                if char == ' ':
                    self.play_file()
                elif self.process_input(char):
                    self.display_matches()
                    if self.check_guess(self.current_input):
                        break

            if not self.unguessed_files:
                break

        self.display_game_over_message()

    def get_char(self) -> str:
        """
        Get a single character input from the user without requiring Enter.

        Returns:
            str: The character entered by the user.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char

    def process_input(self, char: str) -> bool:
        """
        Process the input character and update the game state accordingly.

        Args:
            char (str): The input character.

        Returns:
            bool: True if input should be checked as a guess, False otherwise.
        """
        if char.isalpha():
            self.current_input += char.lower()
            return True
        elif char == '\x7f':  # Backspace
            if self.current_input:
                self.current_input = self.current_input[:-1]
                return True
            return False
        elif char == '\x03':  # Ctrl-C
            print("\nExiting the game.")
            self.stop_audio_and_wait()
            sys.exit(0)
        elif char.isdigit():
            print("Bad input.")
            time.sleep(SLEEP_SECS)
            self.current_input = ""
        return False

    def display_game_state(self):
        """Display the current game state, including song list and progress."""
        self.clear_screen()
        self.display_song_list()
        self.display_progress()
        print("\nPlaying audio... Try to guess the song!")
        print("Press space to replay the audio clip.")

    def display_matches(self):
        """
        Display song titles that match the current input.
        If no matches are found, display "Nope." and reset the input.
        """
        self.clear_screen()
        self.display_song_list()
        self.display_progress()
        print("\nTry to guess the song!")
        print("Press space to replay the audio clip.")

        print(f"\nCurrent input: {self.current_input}")

        if self.current_input:
            matches = [title for title in self.song_titles if title.lower().startswith(self.current_input.lower())]
            if matches:
                print("Matching songs:")
                for match in matches:
                    print(f"- {match}")
            else:
                print("\nNope.")
                time.sleep(SLEEP_SECS)
                self.current_input = ""

    def check_guess(self, guess: str) -> bool:
        """
        Check if the user's guess is correct.

        Args:
            guess (str): The user's guess (concatenated letters).

        Returns:
            bool: True if the guess is correct, False otherwise.
        """
        correct_title = self.get_current_song_title()
        matches = [title for title in self.song_titles if title.lower().startswith(guess.lower())]
        if len(matches) == 1 and matches[0].lower().startswith(guess.lower()):
            if matches[0] == correct_title:
                self.stop_audio_and_wait()
                print("Correct!")
                self.correct_answers += 1
                time.sleep(SLEEP_SECS)
                self.current_input = ""
                return True
            else:
                print("Incorrect guess.")
                time.sleep(SLEEP_SECS)
                self.current_input = ""
        return False

    def get_current_song_title(self) -> Optional[str]:
        """
        Get the title of the currently playing song.

        Returns:
            Optional[str]: The title of the current song, or None if not found.
        """
        return next((title for title, files in self.songs.items() if self.current_file in files), None)

    def select_new_file(self):
        """
        Select a new file to play.
        """
        self.current_file = random.choice(self.unguessed_files)
        self.unguessed_files.remove(self.current_file)

    def play_file(self):
        """
        Play the audio file once in a separate thread.
        """
        self.stop_audio_and_wait()
        self.stop_audio.clear()
        self.audio_thread = threading.Thread(target=self._play_audio_once)
        self.audio_thread.start()

    def _play_audio_once(self):
        """
        Internal method to play audio once.
        """
        sound = pygame.mixer.Sound(self.current_file)
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))
        sound.stop()

    def stop_audio_and_wait(self):
        """
        Stop the audio playback and wait for the audio thread to finish.
        """
        self.stop_audio.set()
        if self.audio_thread:
            self.audio_thread.join()
        self.stop_audio.clear()

    @staticmethod
    def clear_screen():
        """Clear the console screen."""
        os.system('clear')

    # The following methods are not used in interactive mode, but are implemented
    # to satisfy the abstract base class requirements
    def get_user_input(self) -> str:
        return ""

    def handle_guess(self, user_input: str) -> bool:
        return False

    def handle_user_interaction(self) -> bool:
        return False

    def show_answer(self):
        pass


def main():
    """
    Main function to run the Shucks game.

    Parses command-line arguments and initializes the game.
    Accepted command-line arguments:
    -d: Debug mode
    -i or -I: Interactive mode (currently ignored, placeholder for future functionality)
    <integer>: Number of files to use in the game

    The function creates and runs an instance of NormalGameInput with the parsed settings.
    """
    debug_mode = False
    num_files = None
    interactive_switch = False  # This is unused for now, but we'll parse it

    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if arg.lower() == '-d':
            debug_mode = True
        elif arg.lower() in ['-i', '-I']:
            interactive_switch = True  # This is set but not used yet
        elif arg.isdigit():
            num_files = int(arg)

    try:
        if interactive_switch:
            game = InteractiveGameInput(debug_mode, num_files)
        else:
            game = NormalGameInput(debug_mode, num_files)
        game.play()
    except ValueError as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()