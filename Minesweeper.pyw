""" Main """


from src.GUI import *


VERSION = "3.3 Beta3"


def launch():
    """ Game launcher. """
    if check_files():
        MineSweeperGame().start_game()


def set_restart():
    with open("RESTART", "wb") as r:
        r.write(bytes([0]))


if __name__ == "__main__":
    import src.bats

    src.bats.remove_redundant()
    src.bats.rename_to_dat()
    launch()
