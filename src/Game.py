""" Essential part. """

import _tkinter
import random
import threading
import tkinter
import tkinter.messagebox
from time import time, sleep
from src.Helpers import *
from src.Archive import *


class Matrix:
    """ A matrix to record mines.

    ===== Attributes =====
    @param list of list self.matrix:
        An 2D array
    @param int self.rows:
        Number of rows
    @param int self.columns:
        Number of columns
    """

    def __init__(self, rows, columns):
        self.matrix = [[False for _ in range(columns)] for _ in range(rows)]
        self.rows = rows
        self.columns = columns

    def set_mine(self, r, c):
        """ Set (c, r) as a mine. """
        self.matrix[r][c] = True

    def is_mine(self, r, c):
        """ Return True iff (c, r) is a mine. """
        return self.matrix[r][c]

    def count_adj_mines(self, r, c):
        count = 0
        for i in range(max([0, r - 1]), min([r + 2, self.rows])):
            for j in range(max([0, c - 1]), min([c + 2, self.columns])):
                if (i != r or j != c) and self.is_mine(i, j):
                    count += 1
        return count

    def __eq__(self, other):
        """
        @param Matrix self:
        @param Matrix|Any other:
        @rtype: bool
        """
        return isinstance(other, Matrix) and len(other.matrix) == len(self.matrix) and \
            len(other.matrix[0]) == len(self.matrix[0]) and \
            all([self.matrix[r][c] == other.matrix[r][c] for c in range(self.columns) for r in range(self.rows)])


class MineSweeper:
    """ A Minesweeper game.

    ===== Attributes =====
    :param list[list[BlockInfo]] self.records:
    """

    def __init__(self, master, rows, columns, mines):
        """ Inititalize a new MineSweeper.

        @param MineSweeper self:
        @param MineSweeperGame master:
        @param int rows:
        @param int columns:
        @param int mines:
        """
        self.master = master
        self.mines = mines
        self.matrix = Matrix(rows, columns)
        self.flags = Matrix(rows, columns)
        self.remaining = self.mines
        self.time = 0

        res_lst = self.master.cg.configs["resolution"].split("x")
        self.max_width = round(int(res_lst[0]) / 1.5)
        self.max_height = round(int(res_lst[1]) / 1.5)

        self.flag_image = None
        self.wrong_flag_image = None
        self.exp_image = None
        self.qm_image = None
        self.get_resources()

        self.window = tkinter.Toplevel(self.master.root)
        self.window.iconbitmap(self.master.icon)
        self.frame = tkinter.Frame(self.window)
        self.canvas = tkinter.Canvas()
        self.y_scroll = tkinter.Scrollbar()
        self.x_scroll = tkinter.Scrollbar()

        self.top_frame = tkinter.Frame()
        self.count = tkinter.Label()
        self.status = tkinter.Button()
        self.time_frame = tkinter.Label()
        self.show_top_frame()
        self.set_title()

        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        self.menu_bar = tkinter.Menu()
        self.menu_bar.add_command(label=self.master.cg.show(1), command=self.quit)
        self.menu_bar.add_command(label=self.master.cg.show(3), command=self.restart)
        self.window["menu"] = self.menu_bar

        self.records = []
        self.highlight_lines = []

        self.first = True
        self.alive = True
        self.win = False
        self.timer_exist = False
        self.start_time = 0
        self.next_shown = False

    def get_resources(self):
        if self.master.f > 20:
            self.flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "flag_L.png")
            self.wrong_flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "wrong_flag_L.png")
            self.exp_image = tkinter.PhotoImage(file="Resources" + os.sep + "explosion_L.png")
            self.qm_image = tkinter.PhotoImage(file="Resources" + os.sep + "question_L.png")
        elif self.master.f > 14:
            self.flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "flag_M.png")
            self.wrong_flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "wrong_flag_M.png")
            self.exp_image = tkinter.PhotoImage(file="Resources" + os.sep + "explosion_M.png")
            self.qm_image = tkinter.PhotoImage(file="Resources" + os.sep + "question_M.png")
        elif self.master.f > 8:
            self.flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "flag.png")
            self.wrong_flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "wrong_flag.png")
            self.exp_image = tkinter.PhotoImage(file="Resources" + os.sep + "explosion.png")
            self.qm_image = tkinter.PhotoImage(file="Resources" + os.sep + "question.png")
        else:
            self.flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "flag_S.png")
            self.wrong_flag_image = tkinter.PhotoImage(file="Resources" + os.sep + "wrong_flag_S.png")
            self.exp_image = tkinter.PhotoImage(file="Resources" + os.sep + "explosion_S.png")
            self.qm_image = tkinter.PhotoImage(file="Resources" + os.sep + "question_S.png")

    def show_top_frame(self):
        self.top_frame = tkinter.Frame(self.window)

        self.count = tkinter.Label(self.top_frame, text=self.master.cg.show(6) + " " + number_to_string(self.remaining))
        self.count.pack(side="left")
        mid_frame = tkinter.Frame(self.top_frame)
        self.status = tkinter.Button(mid_frame, text="$_$", command=self.restart)
        self.status.pack()
        mid_frame.pack(side="left", expand=True)
        self.time_frame = tkinter.Label(self.top_frame, text=self.master.cg.show(7) + " " + number_to_string(self.time))
        self.time_frame.pack(side="right")

        self.top_frame.pack(fill="x")

    def show_canvas(self):
        self.canvas = tkinter.Canvas(self.frame)
        self.draw_lines()
        self.records = [[BlockInfo() for _ in range(self.matrix.columns)] for _ in range(self.matrix.rows)]
        self.canvas.bind("<Button-1>", self.left_click_handler)
        self.canvas.bind("<ButtonRelease-1>", self.left_release_handler)
        self.canvas.bind("<Button-3>", self.right_click_handler)

        self.canvas.grid(row=0, column=0)
        self.add_scroll_region()

        self.frame.pack()

    def draw_lines(self):
        space = self.get_space()
        for i in range(self.matrix.rows + 2):
            self.canvas.create_line(space, i * space, (self.matrix.columns + 1) * space, i * space)

        for j in range(self.matrix.columns + 2):
            self.canvas.create_line(j * space, space, j * space, (self.matrix.rows + 1) * space)

    def add_scroll_region(self):
        width = self.get_space() * (self.matrix.columns + 2)
        height = self.get_space() * (self.matrix.rows + 2)
        if width > self.max_width:
            self.add_x_scroll()
        else:
            self.canvas.configure(width=width)
        if height > self.max_height:
            self.add_y_scroll()
        else:
            self.canvas.configure(height=height)

    def add_y_scroll(self):
        self.y_scroll = tkinter.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.y_scroll.set)
        self.y_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), height=self.max_height)

        def mouse_wheel_all(event):
            """ Mouse wheel scroll handler of y-direction."""
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

        self.canvas.bind("<MouseWheel>", mouse_wheel_all)

    def add_x_scroll(self):
        self.x_scroll = tkinter.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.x_scroll.set)
        self.x_scroll.grid(row=1, column=0, sticky="we")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=self.max_width)

        def mouse_wheel_x(event):
            """ Mouse wheel scroll handler of x-direction."""
            self.canvas.xview_scroll(-1 * (event.delta // 120), "units")

        self.x_scroll.bind("<MouseWheel>", mouse_wheel_x)

    def left_click_handler(self, event):
        if self.alive and not self.win:
            me = MouseClickEvent(event, self.get_space())

            if me.r < 0 or me.c < 0 or me.r >= self.matrix.rows or me.c >= self.matrix.columns:
                return

            if not self.records[me.r][me.c].checked:
                self.status["text"] = "0v0"
                if self.first:
                    self.first = False
                    self.start_time = time()
                    self.put_mines(me.r, me.c)
                    self.recursive_show(me.r, me.c)
                    self.timing()
                    self.highlight(me.r, me.c, False)
                    return
                if self.matrix.is_mine(me.r, me.c):
                    self.lost()
                else:
                    self.recursive_show(me.r, me.c)
                self.highlight(me.r, me.c, False)

            elif self.records[me.r][me.c].is_number:
                self.status["text"] = "0v0"
                self.show_more(me.r, me.c)
                self.highlight(me.r, me.c, True)

    def left_release_handler(self, event):
        del event
        for line in self.highlight_lines:
            self.canvas.delete(line)
        self.highlight_lines.clear()
        if not self.win and self.check_win():
            self.wining()
        if self.alive:
            if not self.win:
                self.status["text"] = "$_$"
            else:
                self.status["text"] = "^_^"
        else:
            self.status["text"] = "*_*"

    def right_click_handler(self, event):
        if self.alive and not self.win:
            space = self.get_space()
            me = MouseClickEvent(event, space)

            if me.r < 0 or me.c < 0 or me.r >= self.matrix.rows or me.c >= self.matrix.columns:
                return

            pos = (int(space * (me.c + 1.5)), int(space * (me.r + 1.5)))
            if not self.records[me.r][me.c].checked:
                self.put_flag(me.r, me.c)
            elif self.records[me.r][me.c].is_flag:
                flag = self.canvas.find_closest(*pos)
                self.canvas.delete(flag)
                self.flags.matrix[me.r][me.c] = False
                self.put_qm(me.r, me.c)
                self.remaining += 1
            elif self.records[me.r][me.c].is_ques:
                qm = self.canvas.find_closest(*pos)
                self.canvas.delete(qm)
                self.records[me.r][me.c].remove_ques()

            self.count["text"] = self.master.cg.show(6) + " " + number_to_string(self.remaining)

    def put_flag(self, r, c):
        pos = (int(self.get_space() * (c + 1.5)), int(self.get_space() * (r + 1.5)))
        self.canvas.create_image(*pos, image=self.flag_image)
        self.flags.set_mine(r, c)
        self.records[r][c].put_flag()
        self.remaining -= 1

    def put_qm(self, r, c):
        pos = (int(self.get_space() * (c + 1.5)), int(self.get_space() * (r + 1.5)))
        self.canvas.create_image(*pos, image=self.qm_image)
        self.records[r][c].put_ques()

    def single_show(self, r, c):
        space = self.get_space()
        position = (space * (c + 1), space * (r + 1), space * (c + 2), space * (r + 2))
        if self.matrix.is_mine(r, c):
            self.lost()
        number = self.matrix.count_adj_mines(r, c)

        self.records[r][c].put_number()
        self.canvas.create_rectangle(*position, fill="silver")

        if number != 0:
            text_pos = (int(space * (c + 1.5)), int(space * (r + 1.5)))
            color = ""
            if number == 1:
                color = "blue"
            elif number == 2:
                color = "green"
            elif number == 3:
                color = "red"
            elif number == 4:
                color = "navy"
            elif number == 5:
                color = "darkred"
            elif number == 6:
                color = "darkslategray"
            elif number == 7:
                color = "black"
            elif number == 8:
                color = "dimgrey"
            self.canvas.create_text(*text_pos, text=number, font=("Arial", self.master.f), fill=color)

    def show_more(self, r, c):
        if self.matrix.count_adj_mines(r, c) > self.flags.count_adj_mines(r, c):
            return
        elif self.matrix.count_adj_mines(r, c) < self.flags.count_adj_mines(r, c):
            self.lost()
            return
        lst = []
        for i in range(max([0, r - 1]), min([r + 2, self.matrix.rows])):
            for j in range(max([0, c - 1]), min([c + 2, self.matrix.columns])):
                if i != r or j != c:
                    if self.matrix.matrix[i][j] != self.flags.matrix[i][j]:
                        self.lost()
                        return
                    lst.append((i, j))
        [self.recursive_show(t[0], t[1]) for t in lst]

    def all_show(self, lost):
        """ Show all blocks.

        :param bool lost: whether the user losts.
        """
        space = self.get_space()
        if lost:
            for r in range(self.matrix.rows):
                for c in range(self.matrix.columns):

                    pos = (int(space * (c + 1.5)), int(space * (r + 1.5)))
                    if self.matrix.is_mine(r, c) and not self.flags.is_mine(r, c):
                        self.canvas.create_image(*pos, image=self.exp_image)

                    elif self.flags.is_mine(r, c) and not self.matrix.is_mine(r, c):
                        self.canvas.create_image(*pos, image=self.wrong_flag_image)
        else:
            self.remaining = 0
            self.count["text"] = self.master.cg.show(6) + " " + number_to_string(self.remaining)
            for r in range(self.matrix.rows):
                for c in range(self.matrix.columns):
                    if not self.records[r][c].checked:
                        pos = (int(space * (c + 1.5)), int(space * (r + 1.5)))
                        if self.matrix.is_mine(r, c):
                            self.canvas.create_image(*pos, image=self.flag_image)
                        else:
                            self.single_show(r, c)

    def recursive_show(self, r, c):
        """ Show all adjacent blocks until reaches mines."""

        # Iterative approach

        if self.records[r][c].is_flag:
            return
        self.single_show(r, c)
        stack = [(r, c)]

        while len(stack) != 0:
            stack2 = stack.copy()
            stack.clear()
            for point in stack2:
                r1 = point[0]
                c1 = point[1]

                if self.matrix.count_adj_mines(r1, c1) == 0:
                    for i in range(max([0, r1 - 1]), min([r1 + 2, self.matrix.rows])):
                        for j in range(max([0, c1 - 1]), min([c1 + 2, self.matrix.columns])):
                            if (i != r1 or j != c1) and not self.matrix.is_mine(i, j) and not \
                                    self.records[i][j].checked:
                                self.single_show(i, j)
                                stack.append((i, j))

        # Recursive approach
        # This approach may cause memory error when game is very large

        # if not self.records[r][c].checked:
        #     if not self.matrix.is_mine(r, c):
        #         if self.matrix.count_adj_mines(r, c) == 0:
        #             self.single_show(r, c)
        #             for i in range(max([0, r - 1]), min([r + 2, self.matrix.rows])):
        #                 for j in range(max([0, c - 1]), min([c + 2, self.matrix.columns])):
        #                     self.a += 1
        #                     if i != r or j != c:
        #                         self.b += 1
        #                         self.recursive_show(i, j)
        #         else:
        #             self.single_show(r, c)

    def highlight(self, r, c, orig=True):
        space = self.get_space()
        x1 = space * (c + 1) + 1
        y1 = space * (r + 1) + 1
        x2 = space * (c + 2) - 1
        y2 = space * (r + 2) - 1

        self.highlight_lines.append(self.canvas.create_line(x1, y1, x1, y2))
        self.highlight_lines.append(self.canvas.create_line(x1, y1, x2, y1))
        self.highlight_lines.append(self.canvas.create_line(x2, y1, x2, y2))
        self.highlight_lines.append(self.canvas.create_line(x1, y2, x2, y2))

        if orig and self.records[r][c].is_number:

            for i in range(max([0, r - 1]), min([r + 2, self.matrix.rows])):
                for j in range(max([0, c - 1]), min([c + 2, self.matrix.columns])):
                    if (i != r or j != c) and not self.records[i][j].checked:
                        self.highlight(i, j, False)

    def start(self):
        self.show_canvas()

    def quit(self):
        self.master.exist = False
        if (not self.win) and self.alive and (not self.first):
            NewArchive(self).write()
            self.master.set_menu_bar()
        self.window.destroy()

    def next_level(self):
        self.quit()
        self.master.next_level()

    def restart(self):
        self.frame.destroy()
        self.top_frame.destroy()
        self.canvas.destroy()
        self.matrix = Matrix(self.matrix.rows, self.matrix.columns)
        self.flags = Matrix(self.flags.rows, self.flags.columns)
        self.first = True
        self.alive = True
        self.win = False
        self.start_time = time()
        self.time = 0
        self.remaining = self.mines
        self.frame = tkinter.Frame(self.window)
        self.show_top_frame()
        if self.next_shown:
            self.menu_bar.delete(self.master.cg.show(38))
            self.next_shown = False

        self.start()

    def check_win(self):
        """ Return True iff all blocks are"""
        for r in range(self.matrix.rows):
            for c in range(self.matrix.columns):
                if not self.records[r][c].is_number and not self.matrix.is_mine(r, c):
                    return False
        return True

    def wining(self):
        self.all_show(False)
        self.win = True
        if "s" in self.master.mode:
            stage = eval(self.master.mode[1:])
            write_stage(stage, self.time)
            self.master.refresh_stage()
            self.master.right_frame.destroy()
            self.master.fill_right_frame()
            self.master.root.update()
            if self.master.mode != "s30":
                self.next_shown = True
                self.menu_bar.add_cascade(label=self.master.cg.show(38), command=self.next_level)
        elif self.master.mode == "c":
            size = str(self.matrix.rows) + "x" + str(self.matrix.columns) + "x" + str(self.mines)
            write_custom_records(size, self.time)
        else:
            write_record(self.master.mode, self.time)
        tkinter.messagebox.showinfo(title=self.master.cg.show(20), message=self.master.cg.show(35))
        self.window.focus()

    def lost(self):
        self.all_show(True)
        self.alive = False

    def timing(self):
        if not self.timer_exist:
            self.timer_exist = True
            p = threading.Thread(target=self.timer)
            p.setDaemon(True)
            p.start()

    def timer(self):
        while self.alive and not self.win and not self.first:
            try:
                self.time_frame["text"] = self.master.cg.show(7) + " " + number_to_string(self.time)
                self.time = int(time() - self.start_time)
                sleep(0.05)
            except _tkinter.TclError:
                self.timer_exist = False
                return
        self.timer_exist = False

    def put_mines(self, except_r, except_c):
        mines = self.mines
        lst = []
        for i in range(self.matrix.rows * self.matrix.columns):
            lst.append(i)

        lst.remove(except_r * self.matrix.columns + except_c)

        result = []
        while mines > 0:
            to_remove = random.choice(lst)
            result.append(to_remove)
            lst.remove(to_remove)
            mines -= 1

        for mine in result:
            r = mine // self.matrix.columns
            c = mine % self.matrix.columns
            self.matrix.set_mine(r, c)

    def set_title(self):
        if self.master.mode == "e":
            self.window.title(self.master.cg.show(16))
        elif self.master.mode == "m":
            self.window.title(self.master.cg.show(17))
        elif self.master.mode == "h":
            self.window.title(self.master.cg.show(18))
        elif self.master.mode == "c":
            self.window.title(self.master.cg.show(19))
        elif "s" in self.master.mode:
            lev = self.master.mode[1:]
            self.window.title(self.master.cg.show(36) + lev)

    def get_space(self):
        f = self.master.f
        return f * 3


class MouseClickEvent:
    """ A customized mouse event.

    ===== Attributes =====
    :param int pixel_x:
        The pixel-x coordinate on the parent canvas.
    :param int pixel_y:
        The pixel-x coordinate on the parent canvas.
    :param int r:
        The row on the parent canvas.
    :param int c:
        The column on the parent canvas.
    """

    def __init__(self, event, space):
        canvas = event.widget
        self.pixel_x = round(canvas.canvasx(event.x))
        self.pixel_y = round(canvas.canvasy(event.y))
        self.r = (self.pixel_y - space) // space
        self.c = (self.pixel_x - space) // space


class BlockInfo:
    def __init__(self):
        self.info = None
        self.checked = False
        self.is_number = False
        self.is_flag = False
        self.is_ques = False

    def put_flag(self):
        self.is_flag = True
        self.checked = True

    def put_number(self):
        self.checked = True
        self.is_number = True

    def put_ques(self):
        self.checked = True
        self.is_flag = False
        self.is_ques = True

    def remove_ques(self):
        self.is_ques = False
        self.checked = False
