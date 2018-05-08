""" GUI Client. """


import tkinter.messagebox
import tkinter.ttk
from src.ConfigReader import *
from src.Game import *
from Minesweeper import VERSION


class MineSweeperGame:
    """ Game client. """

    def __init__(self):
        self.root = tkinter.Tk()
        self.cg = ConfigGetter()

        self.height_var = tkinter.StringVar()
        self.width_var = tkinter.StringVar()
        self.mines_var = tkinter.StringVar()

        self.custom_top = None
        self.lan_var = tkinter.StringVar()
        self.font_var = tkinter.IntVar()
        self.res_var = tkinter.StringVar()

        self.f = eval(self.cg.configs["font"])
        self.icon = "Resources" + os.sep + "icon.ico"

        self.root.option_add("*Font", "微软雅黑 " + str(self.f))
        self.root.title(self.cg.show(5))
        self.root.iconbitmap(self.icon)
        self.root.resizable(False, False)

        self.size = ()
        self.mode = None
        self.stage_rec = None
        self.last_stage = None
        self.refresh_stage()
        self.stage_list = []
        self.exist = False

        blank = 180 - len(self.cg.show(5)) * 6
        tkinter.Label(self.root, text=self.cg.show(5), font=("微软雅黑", self.f + 12, "bold")). \
            grid(row=0, columnspan=3, padx=blank, pady=10)

        self.fill_left_frame()
        self.right_frame = None
        self.list_box = None
        self.fill_right_frame()

        self.set_menu_bar()

    def set_menu_bar(self):
        menu_bar = tkinter.Menu()
        menu1 = tkinter.Menu(tearoff=0)
        menu1.add_command(label=self.cg.show(2), command=self.settings)
        menu1.add_command(label=self.cg.show(25), command=self.records)
        menu2 = tkinter.Menu(tearoff=0)
        menu2.add_command(label=self.cg.show(26), command=self.version)
        menu2.add_command(label=self.cg.show(27), command=self.show_licence)
        menu_bar.add_cascade(label=self.cg.show(15), menu=menu1)
        menu_bar.add_cascade(label=self.cg.show(24), menu=menu2)
        if os.path.exists("data.msd"):
            menu_bar.add_command(label=self.cg.show(49), command=self.load_last)
        self.root["menu"] = menu_bar

    def refresh_stage(self):
        """ Refresh the stage list.

        @param MineSweeperGame self:
        """
        self.stage_list = []
        self.stage_rec = read_stage()
        self.last_stage = last_stage(self.stage_rec)

    def fill_left_frame(self):
        left_frame = tkinter.Frame(self.root)
        tkinter.Label(left_frame, text=self.cg.show(30), font=("微软雅黑", self.f + 6)).pack(pady=5)
        tkinter.Button(left_frame, text=self.cg.show(16), command=self.easy, width=self.get_button_width(),
                       font=("微软雅黑", self.f + 4, "bold")).pack(pady=5, padx=10)
        tkinter.Button(left_frame, text=self.cg.show(17), command=self.medium, width=self.get_button_width(),
                       font=("微软雅黑", self.f + 4, "bold")).pack(pady=5)
        tkinter.Button(left_frame, text=self.cg.show(18), command=self.hard, width=self.get_button_width(),
                       font=("微软雅黑", self.f + 4, "bold")).pack(pady=5)
        tkinter.Button(left_frame, text=self.cg.show(19), command=self.custom, width=self.get_button_width(),
                       font=("微软雅黑", self.f + 4, "bold")).pack(pady=5)

        tkinter.Label(left_frame).pack()
        left_frame.grid(row=1, column=0, sticky="n")

    def fill_right_frame(self):
        self.right_frame = tkinter.Frame(self.root)
        tkinter.Label(self.right_frame, text=self.cg.show(31), font=("微软雅黑", self.f + 6)).pack(pady=5)

        top = tkinter.Frame(self.right_frame)
        tkinter.Label(top, text=self.cg.show(36)).pack(side="left")
        tkinter.Label(top, text=self.cg.show(37)).pack(side="left", padx=15)
        top.pack(fill="x")

        self.init_stage_games()

        box = tkinter.Frame(self.right_frame)
        sb = tkinter.Scrollbar(box)
        self.list_box = tkinter.Listbox(box, yscrollcommand=sb.set)
        for stage in self.stage_list:
            self.list_box.insert("end", stage.show_title())
            if stage.stage > self.last_stage + 1:
                self.list_box.itemconfigure(stage.stage - 1, fg="gray")
        sb.configure(command=self.list_box.yview)

        sb.pack(side="right", fill="y")
        self.list_box.bind("<Double-Button-1>", self.start_stage_game)
        self.list_box.pack(side="left")
        box.pack()

        tkinter.Label(self.right_frame).pack(pady=10)
        self.right_frame.grid(row=1, column=2, sticky="n")

    def start_stage_game(self, event):
        del event
        if len(self.list_box.curselection()) > 0:
            current_stage = self.list_box.curselection()[0]
            if current_stage <= self.last_stage:
                self.stage_list[current_stage].start_game()

    def easy(self):
        if not self.exist:
            self.size = (9, 9, 10)
            self.mode = "e"
            self.game_start()
        else:
            self.warning()

    def medium(self):
        if not self.exist:
            self.size = (16, 16, 40)
            self.mode = "m"
            self.game_start()
        else:
            self.warning()

    def hard(self):
        if not self.exist:
            self.size = (20, 30, 120)
            self.mode = "h"
            self.game_start()
        else:
            self.warning()

    def custom(self):
        self.custom_top = tkinter.Toplevel(self.root)
        self.custom_top.title(self.cg.show(19))
        self.custom_top.iconbitmap(self.icon)

        upper = tkinter.Frame(self.custom_top)
        tkinter.Label(upper, text=self.cg.show(9), font=("微软雅黑", self.f + 4, "normal")).grid(row=0, column=0)
        height = tkinter.Entry(upper, textvariable=self.height_var, font=("微软雅黑", self.f + 4, "normal"), width=10)
        height.grid(row=0, column=1)
        upper.pack(pady=5)

        mid = tkinter.Frame(self.custom_top)
        tkinter.Label(mid, text=self.cg.show(10), font=("微软雅黑", self.f + 4, "normal")).grid(row=0, column=0)
        width = tkinter.Entry(mid, textvariable=self.width_var, font=("微软雅黑", self.f + 4, "normal"), width=10)
        width.grid(row=0, column=1)
        mid.pack(pady=5)

        lower = tkinter.Frame(self.custom_top)
        tkinter.Label(lower, text=self.cg.show(11), font=("微软雅黑", self.f + 4, "normal")).grid(row=0, column=0)
        mn = tkinter.Entry(lower, textvariable=self.mines_var, font=("微软雅黑", self.f + 4, "normal"), width=10)
        mn.grid(row=0, column=1)
        lower.pack(pady=5)

        tkinter.Button(self.custom_top, text=self.cg.show(4), command=self.custom_start,
                       font=("微软雅黑", self.f + 4, "bold")).pack(padx=60, pady=5)

    def custom_start(self):
        if not self.exist:
            try:
                height = max([2, min([eval(self.height_var.get()), 128])])
                width = max([2, min([eval(self.width_var.get()), 128])])
                mines = max([1, min([eval(self.mines_var.get()), height * width - 2])])

                self.size = (height, width, mines)
                self.mode = "c"
                self.custom_top.destroy()
                self.game_start()
            except SyntaxError:
                self.custom_warning()
                self.custom_top.focus()
        else:
            self.warning()
            self.custom_top.focus()

    def init_stage_games(self):
        for i in range(1, 31):
            self.stage_list.append(StageGame(self, i))

    def game_start(self):
        self.exist = True
        MineSweeper(self, self.size[0], self.size[1], self.size[2]).start()

    def settings(self):
        """ Show the settings panel.

        @param MineSweeperGame self:
        """
        setting = tkinter.Toplevel(self.root)
        setting.title(self.cg.show(2))
        setting.iconbitmap(self.icon)

        tkinter.Label(setting, text="========= " + self.cg.show(2) + " =========").grid(row=0, columnspan=2)
        tkinter.Label(setting, text=self.cg.show(8), font=("微软雅黑", self.f + 2, "normal")).grid(row=1, column=0,
                                                                                               padx=10, pady=5)
        self.lan_var.set("")
        lan_chosen = tkinter.ttk.Combobox(setting, textvariable=self.lan_var, width=12, state="readonly",
                                          font=("微软雅黑", self.f + 2, "normal"))
        lan_chosen["values"] = [key for key in self.cg.lan_dict]
        lan_chosen.current(lan_chosen["values"].index(self.cg.show(100)))
        lan_chosen.grid(row=1, column=1, padx=10)

        tkinter.Label(setting, text=self.cg.show(32), font=("微软雅黑", self.f + 2, "normal")).grid(row=2, column=0,
                                                                                                padx=10, pady=5)
        self.font_var.set(0)
        font_chosen = tkinter.ttk.Combobox(setting, textvariable=self.font_var, width=12, state="readonly",
                                           font=("微软雅黑", self.f + 2, "normal"))
        font_chosen["values"] = [6, 8, 10, 12, 14, 16, 20, 24]
        cur_font = str(self.f)
        font_chosen.current(font_chosen["values"].index(cur_font))
        font_chosen.grid(row=2, column=1, padx=10)

        tkinter.Button(setting, text=self.cg.show(14), command=self.setting_confirm,
                       font=("微软雅黑", self.f + 2, "bold")).grid(row=4, columnspan=2, pady=5, ipadx=20)

        tkinter.Label(setting, text=self.cg.show(43), font=("微软雅黑", self.f + 2, "normal")).grid(row=3, column=0,
                                                                                                padx=10, pady=5)

        self.res_var.set("")
        res_chosen = tkinter.ttk.Combobox(setting, textvariable=self.res_var, width=12, state="readonly",
                                          font=("微软雅黑", self.f + 2, "normal"))
        res_chosen["values"] = ["1280x720", "1366x768", "1600x900", "1920x1080", "2560x1440", "3840x2160"]
        cur_res = self.cg.configs["resolution"]
        res_chosen.current(res_chosen["values"].index(cur_res))
        res_chosen.grid(row=3, column=1, padx=10)

    def setting_confirm(self):
        language = self.lan_var.get()
        lan_code = self.cg.lan_dict[language]
        resolution = self.res_var.get()
        self.cg.set("language", lan_code)
        self.cg.set("font", str(self.font_var.get()))
        self.cg.set("resolution", resolution)

        self.cg.save()

        temp_cg = ConfigGetter()
        tkinter.messagebox.showinfo(title=temp_cg.show(14), message=temp_cg.show(29))

        self.root.quit()

    def records(self):
        top = tkinter.Toplevel(self.root)
        top.title(self.cg.show(25))
        top.iconbitmap(self.icon)

        tkinter.Label(top, text=self.cg.show(28), font=("微软雅黑", self.f + 4, "bold")). \
            grid(row=0, columnspan=2, padx=60, pady=5)
        current_rec = read_record()
        tkinter.Label(top, text=self.cg.show(16) + ": ", font=("微软雅黑", self.f + 4, "normal")). \
            grid(row=1, column=0, pady=5)
        tkinter.Label(top, text=current_rec[0], font=("微软雅黑", self.f + 4, "normal")).grid(row=1, column=1)
        tkinter.Label(top, text=self.cg.show(17) + ": ", font=("微软雅黑", self.f + 4, "normal")). \
            grid(row=2, column=0, pady=5)
        tkinter.Label(top, text=current_rec[1], font=("微软雅黑", self.f + 4, "normal")).grid(row=2, column=1)
        tkinter.Label(top, text=self.cg.show(18) + ": ", font=("微软雅黑", self.f + 4, "normal")). \
            grid(row=3, column=0, pady=5)
        tkinter.Label(top, text=current_rec[2], font=("微软雅黑", self.f + 4, "normal")).grid(row=3, column=1)

        menu = tkinter.Menu(top)
        menu.add_command(label=self.cg.show(47), command=self.custom_records)
        top["menu"] = menu

    def custom_records(self):
        top = tkinter.Toplevel(self.root)
        top.title(self.cg.show(47))

        tkinter.Label(top, text=self.cg.show(47), font=("微软雅黑", self.f + 4, "bold")).pack(pady=10)

        lst = [item.split("=")[0].split("x") + [item[:-1].split("=")[1]] for item in to_list(read_custom_records())]

        unit_width = int(self.cg.show(101))
        size_label = self.cg.show(48)
        mine_label = self.cg.show(11)[:-1]
        time_label = self.cg.show(7)[:-1]
        gap1 = 16 - len(size_label) * unit_width * 2
        gap2 = 14 - len(mine_label) * unit_width * 2
        title = str.format("{}{}{}{}{}", size_label, " " * gap1, mine_label, " " * gap2, time_label)

        tkinter.Label(top, text=title).pack(anchor="w", padx=10)

        frame = tkinter.Frame(top)
        sb = tkinter.Scrollbar(frame)
        listbox = tkinter.Listbox(frame, yscrollcommand=sb.set)

        for group in lst:
            space1 = 16 - (len(group[0]) + len(group[1])) * 2
            space2 = 10 - len(group[2]) * 2
            string = str.format("{}{}{}{}{}{}{}", group[0], "x", group[1], " " * space1, group[2], " " * space2,
                                group[3] + " " + self.cg.show(39))
            listbox.insert("end", string)
        sb.configure(command=listbox.yview)
        listbox.pack(side="left")
        sb.pack(side="right", fill="y")
        frame.pack(padx=10)
        tkinter.Label(top).pack()

    def version(self):
        """ Show the infomation about this software.

        @param MineSweeperGame self:
        """
        ver = tkinter.Toplevel(self.root)
        ver.title(self.cg.show(24))
        ver.iconbitmap(self.icon)

        tkinter.Label(ver, text=self.cg.show(5), font=("微软雅黑", self.f + 4, "normal")).pack(pady=5, padx=70)
        tkinter.Label(ver, text="v" + VERSION, font=("微软雅黑", self.f, "normal")).pack(padx=70)
        tkinter.Label(ver, text=self.cg.show(42), font=("微软雅黑", self.f, "normal")).pack(padx=70)
        tkinter.Label(ver).pack()

    def show_licence(self):
        lic = tkinter.Toplevel(self.root)
        lic.title(self.cg.show(5))
        lic.iconbitmap(self.icon)

        with open("Licence.txt", "r") as file:
            text_ = file.read()

        tkinter.Label(lic, text=text_).pack(pady=5, padx=10)
        tkinter.Label(lic).pack()

    def start_game(self):
        self.root.mainloop()

    def restart(self):
        MineSweeper(self, self.size[0], self.size[1], self.size[2]).start()

    def next_level(self):
        cur = eval(self.mode[1:])
        self.stage_list[cur].start_game()

    def get_button_width(self):
        return round(self.f ** 0.3 * 5)

    def load_last(self):
        data = OldArchive()
        self.mode = data.mode
        game = MineSweeper(self, data.rows, data.columns, data.total)
        game.first = False
        game.start_time = time() - data.time_used
        game.timing()
        game.start()
        data.set_game(game)
        os.remove("data.msd")
        self.set_menu_bar()

    def warning(self):
        tkinter.messagebox.showwarning(title=self.cg.show(33), message=self.cg.show(34))

    def custom_warning(self):
        tkinter.messagebox.showwarning(title=self.cg.show(40), message=self.cg.show(41))


class StageGame:
    """ A stage game

    ===== Attributes =====
    @param MineSweeperGame master:
        master
    """

    def __init__(self, master, stage):
        self.master = master
        self.stage = stage
        if stage <= 15:
            self.r = 10 + round(stage / 3)
            self.c = 10 + round(stage / 3)
            self.m = round(self.r * self.c / (15 - stage * 0.6))
        else:
            self.r = 15 + round((stage - 15) / 2)
            self.c = stage
            self.m = round(self.r * self.c / (6 - (stage - 15) * 0.12))

    def start_game(self):
        if not self.master.exist:
            self.master.mode = "s" + str(self.stage)
            self.master.exist = True
            game = MineSweeper(self.master, self.r, self.c, self.m)
            game.start()
        else:
            self.master.warning()

    def is_passed(self):
        return self.master.last_stage >= self.stage

    def show_title(self):
        string = str(self.stage) + " " * 8
        for i in range(3 - len(str(self.stage))):
            string += "  "
        if self.is_passed():
            string += self.master.stage_rec[str(self.stage)] + " " + self.master.cg.show(39)
        else:
            string += "N/A"
        return string
