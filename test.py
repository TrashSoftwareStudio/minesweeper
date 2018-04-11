import tkinter
import os


def ff():
    if os.name == "nt":
        from win32api import GetSystemMetrics
        width = GetSystemMetrics(0)
        height = GetSystemMetrics(1)
        print(width, height)

    root = tkinter.Tk()

    outer_frame = tkinter.Frame(root)
    canvas = tkinter.Canvas(outer_frame)
    frame = tkinter.Frame(canvas)

    for i in range(20):
        tkinter.Label(frame, text="ggg").pack()

    sb = tkinter.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)

    canvas.pack(side="left")
    sb.pack(side="right", fill="y")

    def bind_to(event):
        canvas.configure(scrollregion=canvas.bbox("all"), width=100, height=100)

    canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", bind_to)

    outer_frame.pack()

    root.mainloop()


def n_de_n1(n):
    i = 0
    while i < n ** n:
        i += 1
    return i


def n_de_n2(n):
    i = 0
    lst = [x for x in range(n)]
    while i < n:
        j = 0
        while j < n:
            lst += [x for x in range(len(lst))]
            j += 1
        i += 1
    return len(lst)


if __name__ == "__main__":
    # import time
    # ff()
    # a = n_de_n1(3)
    # print(a)
    # b = n_de_n2(3)
    # print(b)
    # print(b / a)
    import sys
    import os
    from tkinter import Tk, Label, Button


    def restart_program():
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = sys.executable
        os.execl(python, python, *sys.argv)


    root = Tk()

    Label(root, text="Hello World!").pack()
    Button(root, text="Restart", command=restart_program).pack()

    root.mainloop()

