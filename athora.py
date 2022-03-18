import os.path
import sys
import textwrap
import logic
import colorama
from movement.map import choose_map, get_map
from colorama import Fore

# Initialise ANSI escape colour codes for Windows
colorama.init()


def main():
    # Get command line args
    args = sys.argv[1:]

    # Print game title
    title = textwrap.dedent(f"""
                Hello. Welcome to
                                    
                       d8888 888    888
                      d88888 888    888
                     d88P888 888    888
                    d88P 888 888888 88888b.   .d88b.  888d888 8888b.
                   d88P  888 888    888 "88b d88""88b 888P"      "88b
                  d88P   888 888    888  888 888  888 888    .d888888
                 d8888888888 Y88b.  888  888 Y88..88P 888    888  888
                d88P     888  "Y888 888  888  "Y88P"  888    "Y888888  {Fore.YELLOW}py-v2.0.0{Fore.RESET}
                """)

    print(title)

    while True:
        # Check if a map was provided in CMD args, and if so,
        # start the game with that map. Otherwise, allow the user
        # to choose a map.
        if len(args) > 0:
            print(f"Loading map from file...")
            logic.start_game(get_map(args[0]))
            args.clear()
        else:
            maps_path = os.path.dirname(os.path.realpath(__file__)) + "/maps/"
            chosen_map = choose_map(maps_path)
            if chosen_map is not None:
                logic.start_game(get_map(chosen_map))
            else:
                break


if __name__ == '__main__':
    main()