from playsound import playsound
import os
import random
import time
import sys

DEBUG = 0  # Set to 1 to enable debug mode

def play_file(path_string: str):
    """
    Play the .mp3 file located at the `path_string` argument through
    the computer's headphone jack.
    :param path_string: the string path to an mp3 file
    :return: None
    """
    playsound(path_string)

def get_songs(debug_mode=False):
    """
    Read the contents of the audio_files directory and convert filenames to song titles.
    :param debug_mode: If True, return only five audio clips
    :return: A dictionary mapping song titles to a list of audio file paths
    """
    songs = {}
    audio_dir = "audio_files"

    for filename in os.listdir(audio_dir):
        if filename.endswith(".mp3"):
            name_without_ext = os.path.splitext(filename)[0]
            words = name_without_ext.split('_')
            song_title = ' '.join(word.capitalize() for word in words[:-1])
            audio_path = os.path.join(audio_dir, filename)
            songs.setdefault(song_title, []).append(audio_path)

    if debug_mode:
        # Select only five audio clips for debug mode
        songs = {title: paths[:1] for title, paths in list(songs.items())[:5]}

    return songs

def clear_screen():
    """Clear the console screen."""
    if os.name == 'nt':
        os.system('cls')
    else:
        print('\033[H\033[J', end='')

def print_song_list(songs):
    """Print the numbered list of songs."""
    print("List of songs:")
    for i, song in enumerate(songs, 1):
        print(f"{i}. {song}")

def get_valid_input(songs):
    """
    Prompt the user for input and validate it.
    :param songs: List of song titles
    :return: Valid user input (number, 's', 'S', 'a', 'A', 'r', 'R', 'q', 'Q')
    """
    valid_inputs = [str(i) for i in range(1, len(songs) + 1)] + ['s', 'S', 'a', 'A', 'r', 'R', 'q', 'Q']
    while True:
        user_input = input("\nEnter your choice: ")
        if user_input in valid_inputs:
            return user_input
        else:
            clear_screen()
            print("Invalid input. Please try again.")
            print_song_list(songs)  # Pass the song_titles list to print_song_list

def display_guess(user_guess, song_titles, correct_answer):
    """
    Display the user's guess, the correct answer (if in debug mode), and the list of song titles.
    :param user_guess: The user's guess (song number or action)
    :param song_titles: List of song titles
    :param correct_answer: The correct song title (if in debug mode)
    """
    clear_screen()
    if correct_answer:
        print(f"Correct answer: {correct_answer}\n")
    if user_guess is not None:
        if user_guess.isdigit():
            song_index = int(user_guess) - 1
            print(f"Your incorrect guess was: {song_titles[song_index]}\n")
        else:
            print(f"Your incorrect guess was: {user_guess}\n")
    print_song_list(song_titles)

def handle_guess(user_input, current_file, songs, song_titles, unguessed_files):
    """
    Handle the user's guess or action.
    :param user_input: The user's input (song number or action)
    :param current_file: The current audio file being played
    :param songs: Dictionary mapping song titles to audio file paths
    :param song_titles: List of song titles
    :param unguessed_files: List of unguessed audio file paths
    :return: A tuple containing a boolean indicating whether to continue the loop, and the updated current_file
    """
    if user_input.lower() == 'q':
        return False, None
    elif user_input.lower() == 's':
        # Skip the current audio file
        unguessed_files.append(current_file)
        current_file = random.choice(unguessed_files)
    elif user_input.lower() == 'a':
        # Display the correct answer
        song_title = [title for title, paths in songs.items() if current_file in paths][0]
        print(f"\nThe correct song is: {song_title}")
        time.sleep(2)
        unguessed_files.append(current_file)  # Add the audio clip back to unguessed files
        current_file = random.choice(unguessed_files)
    elif user_input.lower() == 'r':
        # Replay the current audio file
        play_file(current_file)
        return True, current_file
    else:
        # User guessed a song number
        user_guess = int(user_input) - 1
        song_title = song_titles[user_guess]
        if current_file in songs[song_title]:
            print(f"\nCorrect! The audio clip is from {song_title}.")
            time.sleep(2)
            unguessed_files.remove(current_file)
            current_file = random.choice(unguessed_files)
        else:
            correct_answer = [title for title, paths in songs.items() if current_file in paths][0]
            display_guess(user_input, song_titles, correct_answer)
            print("\nIncorrect. Try again.")

    return True, current_file

def main():
    debug_mode = DEBUG or "-d" in sys.argv

    songs = get_songs(debug_mode)
    song_titles = list(songs.keys())
    print_song_list(song_titles)

    # Keep track of unguessed audio files
    unguessed_files = []
    for file_paths in songs.values():
        unguessed_files.extend(file_paths)

    current_file = None
    prev_file = None

    while unguessed_files:
        if not current_file or (debug_mode and current_file != prev_file):
            # Choose a new audio file at random from unguessed files
            current_file = random.choice(unguessed_files)
            if debug_mode:
                correct_answer = [title for title, paths in songs.items() if current_file in paths][0]
                display_guess(None, song_titles, correct_answer)
                print("\nPlaying audio...")
            prev_file = current_file

        else:
            print(f"\nPlaying audio...")

        play_file(current_file)

        user_input = get_valid_input(song_titles)
        continue_loop, current_file = handle_guess(user_input, current_file, songs, song_titles, unguessed_files)

        if not continue_loop:
            break

if __name__ == "__main__":
    main()