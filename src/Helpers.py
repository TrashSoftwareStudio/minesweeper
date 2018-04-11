""" Helper functions. """


import base64
import os
import tkinter.messagebox


RECORDS = "records.dat"
STAGES = "stages.dat"
CUSTOMS = "customs.dat"


def check_files():
    """ Return True iff all required files exist.

    @rtype: bool
    """
    # Directory list
    d_list = ["Languages", "Resources"]

    # Files in \Resources
    f_list = ["explosion.png", "explosion_S.png", "explosion_M.png", "explosion_L.png",
              "flag.png",  "flag_S.png", "flag_M.png", "flag_L.png",
              "wrong_flag.png", "wrong_flag_S.png", "wrong_flag_M.png", "wrong_flag_L.png",
              "question.png", "question_S.png", "question_M.png", "question_L.png",
              "icon.ico"]

    # Check directories
    miss = False
    missing_d = []
    for d in d_list:
        if not os.path.exists(d):
            miss = True
            missing_d.append(d)

    # Check files
    missing_f = []
    for f in f_list:
        if not os.path.exists("Resources" + os.sep + f):
            miss = True
            missing_f.append(f)

    if miss:
        missing_files(missing_d, missing_f)
        return False
    else:
        return True


def missing_files(d_list, f_list):
    """ Throw a message box contains missing directories and files. """
    missing = "Missing directories: \n"
    for d in d_list:
        missing += d + "\n"
    missing += "Missing files: \n"
    for f in f_list:
        missing += f + "\n"
    if "Languages" not in d_list and len(os.listdir("Languages")) == 0:
        missing += "Language files\n"
    tkinter.messagebox.showerror(title="Error", message=missing)


def number_to_string(number):
    """ Return a string containing 3-digits translated from int number.

    Precondition: 0 <= number

    @param int number:
    @rtype: str
    """
    length = len(str(number))
    result = ""
    for i in range(3-length):
        result += "0"
    return result + str(number)


def read_record():
    """ Return a list of 3 int which represents the record of mode e, m, h from records.dat if it exists.
    Otherwise, create this file.

    @rtype: list
    """
    if os.path.exists(RECORDS):
        with open(RECORDS, "rb") as infile:
            data = infile.read()
        dec = base64.decodebytes(data)
        string = dec.decode(encoding="utf-8")
        records = string.split("\n")[:-1]
        return records
    else:
        rec = "999\n"
        rec += "999\n"
        rec += "999\n"
        with open(RECORDS, "wb") as infile:
            data = rec.encode(encoding="utf-8")
            encoded = base64.encodebytes(data)
            infile.write(encoded)
        return read_record()


def write_record(mode, rec_time):
    """ Write the new records <rec_time> of <mode> to records.db if rec_time < the old record.

    @param str mode:
    @param int rec_time:
    @rtype: NoneType
    """
    rec = read_record()
    if mode == "e":
        if rec_time < eval(rec[0]):
            rec[0] = str(rec_time)
    elif mode == "m":
        if rec_time < eval(rec[1]):
            rec[1] = str(rec_time)
    elif mode == "h":
        if rec_time < eval(rec[2]):
            rec[2] = str(rec_time)

    string = rec[0] + "\n"
    string += rec[1] + "\n"
    string += rec[2] + "\n"

    with open(RECORDS, "wb") as infile:
        data = string.encode(encoding="utf-8")
        encoded = base64.encodebytes(data)
        infile.write(encoded)


def read_custom_records():
    """ Read all records of custom games.

    :rtype: dict
    """
    if os.path.exists(CUSTOMS):
        with open(CUSTOMS, "rb") as f:
            data = f.read()
        d = {}
        dec = base64.decodebytes(data)
        string = dec.decode(encoding="utf-8")
        lines = string.split("\n")[:-1]
        for line in lines:
            sp = line.split("=")
            d[sp[0]] = int(sp[1])
        return d
    else:
        data = "".encode(encoding="utf-8")
        encoded = base64.encodebytes(data)
        with open(CUSTOMS, "wb") as f:
            f.write(encoded)
        return {}


def write_custom_records(size: str, time: int):
    """
    Write a new custom game game record if the new record is faster than the previous record of the same game size.

    :param str size: the game size.
    :param int time: time of the game
    :return: None
    """
    current = read_custom_records()
    if size in current:
        if time < current[size]:
            current[size] = time
    else:
        current[size] = time

    lst = to_list(current)
    string = "".join(lst)
    data = string.encode(encoding="utf-8")
    encoded = base64.encodebytes(data)
    with open(CUSTOMS, "wb") as f:
        f.write(encoded)


def to_list(record: dict):
    """
    Return a sorted list of all keys and elements in record.

    :rtype list(str)
    """
    def get_sort(a: str):
        x = a.split("=")[0].split("x")
        return int(x[0]) * int(x[1]) + int(x[2]) / 10

    lst = [key + "=" + str(record[key]) + "\n" for key in record]
    lst.sort(key=get_sort)
    return lst


def read_stage():
    """  Read the records of stage games and return dict{stage: time}.

    @rtype: dict
    """
    if os.path.exists(STAGES):
        d = {}
        with open(STAGES, "rb") as infile:
            data = infile.read()
        dec = base64.decodebytes(data)
        string = dec.decode(encoding="utf-8")
        records = string.split("\n")[:-1]
        for rec in records:
            sub = rec.split(" = ")
            d[sub[0]] = sub[1]
        return d
    else:
        rec = "0 = 999\n"
        with open(STAGES, "wb") as infile:
            data = rec.encode(encoding="utf-8")
            encoded = base64.encodebytes(data)
            infile.write(encoded)
        return read_stage()


def write_stage(stage, rec_time):
    """ Write stage to stage.dat

    @param int stage:
    @param int rec_time:
    @rtype: NoneType
    """
    old = read_stage()
    if last_stage(old) >= stage:
        if eval(old[str(stage)]) > rec_time:
            old[str(stage)] = str(rec_time)
    else:
        old[str(stage)] = str(rec_time)

    lst = []
    for i in range(1, 101):
        if str(i) in old:
            sub = str(i) + " = " + old[str(i)] + "\n"
            lst.append(sub)
        else:
            break

    string = str.join("", lst)
    with open(STAGES, "wb") as infile:
        data = string.encode(encoding="utf-8")
        encoded = base64.encodebytes(data)
        infile.write(encoded)


def last_stage(stages):
    """ Return the highest stage in stages.

    @param dict stages:
    @rtype: int
    """
    return max([eval(stage) for stage in stages])
