from src.Helpers import number_to_string


def bits_to_byte(string):
    """

    :param str string:
    :return:
    """
    assert len(string) == 8
    num = sum([int(string[i]) << (7 - i) for i in range(8)])

    return num.to_bytes(1, "big")[0]


def byte_to_bits(b):
    """

    :param int b:
    :return:
    """
    s = "{0:b}".format(b)
    return "0" * (8 - len(s)) + s


def int_to_bytes(num):
    """

    :param int num:
    :return:
    """
    return num.to_bytes(4, "big")


def mode_to_bytes(mode):
    """

    :param str mode:
    :return:
    """
    res = []
    modes = ["e", "m", "h", "c"]
    if mode in modes:
        res.append(modes.index(mode))
        res.append(0)
    else:
        res.append(4)
        res.append(eval(mode[1:]))

    return bytes(res)


def bytes_to_mode(b):
    """

    :param bytes b:
    :return:
    """
    modes = ["e", "m", "h", "c"]
    if (b[0] & 0xff) == 4:
        return "s" + str(b[1] & 0xff)
    else:
        return modes[b[0] & 0xff]


class NewArchive:
    """
    Save a game into an archive.
    """
    def __init__(self, game):
        """

        :param src.Game.MineSweeper game:
        """
        rows = game.matrix.rows
        columns = game.matrix.columns
        total = game.mines
        time_used = game.time

        result = []
        result += int_to_bytes(rows)
        result += int_to_bytes(columns)
        result += int_to_bytes(total)
        result += int_to_bytes(time_used)

        mode = game.master.mode
        result += mode_to_bytes(mode)

        a_byte = []
        for r in range(rows):
            for c in range(columns):
                if game.matrix.is_mine(r, c):
                    a_byte.append('1')
                else:
                    a_byte.append('0')

                if game.records[r][c].checked:
                    a_byte.append('1')
                    if game.records[r][c].is_flag:
                        a_byte.append('1')
                        a_byte.append('0')
                    else:
                        a_byte.append('0')
                        if game.records[r][c].is_ques:
                            a_byte.append('1')
                        else:
                            a_byte.append('0')
                else:
                    a_byte.append('0')
                    a_byte.append('0')
                    a_byte.append('0')

                if len(a_byte) == 8:
                    s = "".join(a_byte)
                    result.append(bits_to_byte(s))
                    a_byte.clear()

        if len(a_byte) == 8:
            s = "".join(a_byte)
            result.append(bits_to_byte(s))
        elif len(a_byte) == 4:
            s = "".join(a_byte) + "0000"
            result.append(bits_to_byte(s))

        self.data = bytes(result)

    def write(self):
        with open("data.msd", "wb") as f:
            f.write(self.data)


class OldArchive:
    """
    An archive read from saved data.
    """
    def __init__(self):
        """
        """
        with open("data.msd", "rb") as f:
            self.rows = int.from_bytes(f.read(4), "big")
            self.columns = int.from_bytes(f.read(4), "big")
            self.total = int.from_bytes(f.read(4), "big")
            self.time_used = int.from_bytes(f.read(4), "big")
            self.mode = bytes_to_mode(f.read(2))

            self.data = f.read()

    def set_game(self, game):
        """

        :param src.Game.MineSweeper game:
        :return:
        """
        lst = []
        for b in self.data:
            s = byte_to_bits(b)
            front = s[:4]
            back = s[4:]
            lst.append(front)
            lst.append(back)

        i = 0
        for r in range(self.rows):
            for c in range(self.columns):
                inf = lst[i]
                i += 1
                if inf[0] == '0':
                    game.matrix.matrix[r][c] = False
                else:
                    game.matrix.set_mine(r, c)
        j = 0
        for r in range(self.rows):
            for c in range(self.columns):
                inf = lst[j]
                j += 1
                if inf[1] == '1':
                    if inf[2] == '1':
                        game.records[r][c].put_flag()
                        game.put_flag(r, c)
                    else:
                        if inf[3] == '1':
                            game.records[r][c].put_ques()
                            game.put_qm(r, c)
                        else:
                            game.single_show(r, c)
        game.count["text"] = game.master.cg.show(6) + " " + number_to_string(game.remaining)


if __name__ == "__main__":
    print(byte_to_bits(23))
