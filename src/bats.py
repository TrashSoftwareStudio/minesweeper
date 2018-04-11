"""Bats using for updates"""


import os


def remove_redundant():
    lst = ["explosion.png", "flag.png", "wrong_flag.png"]
    for file in lst:
        if os.path.exists(file):
            os.remove(file)


def rename_to_dat():
    if os.path.exists("records.db"):
        os.rename("records.db", "records.dat")
    if os.path.exists("stages.db"):
        os.rename("stages.db", "stages.dat")
