from playsound import playsound
import os


def play_file(path_string: str):
    """
    Play the .mp3 file located at the `path_string` argument through
    the computer's headphone jack.
    :param path_string: the string path to an mp3 file
    :return: None
    """
    playsound(path_string)


def get_songs():
    """
    Read the contents of the audio_files directory and convert filenames to song titles.
    :return: A list of song titles
    """
    songs = []
    audio_dir = "audio_files"

    for filename in os.listdir(audio_dir):
        if filename.endswith(".mp3"):
            name_without_ext = os.path.splitext(filename)[0]
            words = name_without_ext.split('_')
            song_title = ' '.join(word.capitalize() for word in words[:-1])
            songs.append(song_title)

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
    :return: Valid user guess as an integer
    """
    while True:
        user_input = input("\nEnter the number of the song you think this is: ")
        try:
            user_guess = int(user_input)
            if 1 <= user_guess <= len(songs):
                return user_guess
            else:
                raise ValueError
        except ValueError:
            clear_screen()
            print("Invalid input. Please enter a valid song number.\n")
            print_song_list(songs)


def main():
    songs = get_songs()
    print_song_list(songs)

    # Play the audio file
    audio_file = "beaver_breath_opening.mp3"
    audio_path = os.path.join("audio_files", audio_file)
    print("\nPlaying audio...")
    play_file(audio_path)

    user_guess = get_valid_input(songs)
    print(f"\nYou guessed: {songs[user_guess - 1]}")


if __name__ == "__main__":
    main()