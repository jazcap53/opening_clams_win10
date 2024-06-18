from playsound import playsound


def play_file(path_string: str):
    """
    Play the .mp3 file located at its `path_string` argument through
    the computer's headphone jack.
    :param path_string: the string path to an mp3 file
    :return: None
    """
    playsound(path_string)


