""" Config reader and writter. """


import os


class ConfigGetter:
    """ Get and set configs.

    ===== Attributes =====
    @param dict self.configs:
        Configs read from pref.ini.
    """
    def __init__(self):
        self.configs = {}
        self.language = {}
        self.lan_dict = {}
        self.read_config()
        self.read_lan()

    def read_config(self):
        if os.path.exists("pref.ini"):
            with open("pref.ini", "r") as pref:
                text_lst = pref.read().split("\n")[:-1]
            for line in text_lst:
                line_lst = line.split("=")
                self.configs[line_lst[0]] = line_lst[1]
            self.check_config()
        else:
            self.check_config()
            self.save()

    def check_config(self):
        default_configs = {"language": "chs", "font": "10", "resolution": "1920x1080"}
        for item in default_configs:
            if item not in self.configs:
                self.set(item, default_configs[item])

    def read_lan(self):
        with open("Languages" + os.sep + self.configs["language"] + ".txt", "r", encoding="utf-8") as lan_pack:
            text_lst = lan_pack.read().split("\n")[:-1]
        for line in text_lst:
            line_lst = line.split("=")
            if "\ufeff" in line_lst[0]:
                line_lst[0] = line_lst[0][1:]
            self.language[line_lst[0]] = line_lst[1]

        lan_file_list = os.listdir("Languages")
        for lan in lan_file_list:
            with open("Languages" + os.sep + lan, "r", encoding="utf-8") as lan_pack:
                first = lan_pack.readline()
                language = first.split("=")[1][:-1]
                self.lan_dict[language] = lan[:-4]

    def show(self, code):
        """ Show the text for the code from the current language.

        @param ConfigGetter self:
        @param int code:
        @rtype: str
        """
        return self.language[str(code)].replace("\\", "\n")

    def set(self, key, value):
        self.configs[key] = value

    def save(self):
        result = ""
        for key in self.configs:
            line = key + "=" + self.configs[key] + "\n"
            result += line
        with open("pref.ini", "w") as file:
            file.write(result)
