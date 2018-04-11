""" Main """


from src.GUI import *


VERSION = "3.3 Beta2"


def launch():
    """ Game launcher. """
    if check_files():
        MineSweeperGame().start_game()


def set_restart():
    with open("RESTART", "wb") as r:
        r.write(bytes([0]))


# def restart_window():
#     """ Restart the program. """
#     os.remove("RESTART")
#     subprocess.call(sys.executable + ' "' + os.path.realpath("Minesweeper.pyw") + '"')


if __name__ == "__main__":
    import src.bats

    src.bats.remove_redundant()
    src.bats.rename_to_dat()
    launch()
    # if os.path.exists("RESTART"):
    #     restart_window()
