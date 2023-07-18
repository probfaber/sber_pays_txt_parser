import traceback
import os.path
import json
from threading import Thread
from tkinter import Tk, END, NORMAL, DISABLED, Label, Entry, Button, W, E, CENTER
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from sber_pays_txt_parser import main as parse

VER = "2023-07-18"
TITLE = "Парсер платёжек Сбербанка v.{}".format(VER)
conf = {}
CONF_FILE_NAME = "conf.txt"
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_FILE = os.path.join(CUR_DIR, CONF_FILE_NAME)


def read_conf():
    global conf
    ff = CONF_FILE
    if os.path.exists(ff):
        with open(ff, "r") as f:
            conf = json.load(f)
    else:
        conf = {"inp_dir": "", "out_dir": ""}

    edt_inp.delete(0, END)
    edt_inp.insert(0, conf.get("inp_dir", ""))

    edt_out.delete(0, END)
    edt_out.insert(0, conf.get("out_dir", ""))


def write_conf():
    global conf
    conf["inp_dir"] = edt_inp.get()
    conf["out_dir"] = edt_out.get()
    ff = CONF_FILE
    with open(ff, "w") as f:
        json.dump(conf, f, ensure_ascii=False, indent=4)


def choose_inp(ev):
    val = filedialog.askdirectory()
    if val == '':
        return
    edt_inp.delete(0, END)
    edt_inp.insert(0, val)


def choose_out(ev):
    val = filedialog.askdirectory()
    if val == '':
        return
    edt_out.delete(0, END)
    edt_out.insert(0, val)


def parse_wrapper(inp, out):
    parse(inp, out)
    done_action()


def done_action():
    pb.stop()
    btn_start.config(state=NORMAL)
    messagebox.showinfo(message="завершено")


def start(ev):
    inp = edt_inp.get()
    out = edt_out.get()

    if not os.path.exists(inp):
        messagebox.showinfo(message="Путь {} не существует".format(inp))
        return
    if not os.path.exists(out):
        messagebox.showinfo(message="Путь {} не существует".format(out))
        return

    btn_start.config(state=DISABLED)
    t = Thread(target=parse_wrapper, args=(inp, out))
    t.start()
    pb.start()


def show_error(self, *args):
    err = traceback.format_exception(*args)
    messagebox.showerror('Exception', err)


# при закрытии окна выполняется
def on_delete_window():
    try:
        write_conf()
    except Exception:
        pass

    try:
        root.destroy()
    except Exception:
        pass


root = Tk()
root.protocol("WM_DELETE_WINDOW", on_delete_window)
Tk.report_callback_exception = show_error
win_width = 800
win_height = 320
root.minsize(win_width, win_height)
root.maxsize(win_width, win_height)
root.title(TITLE)

positionRight = int(root.winfo_screenwidth() / 2 - win_width / 2)
positionDown = int(root.winfo_screenheight() / 2.5 - win_height / 2)

root.geometry("{}x{}+{}+{}".format(win_width, win_height, positionRight, positionDown))

Label(root, text="Загрузить из папки").grid(row=0, column=0, sticky=W, padx=10, pady=20)
Label(root, text="Выгрузить в папку").grid(row=1, column=0, sticky=W, padx=10)

edt_inp = Entry(root, width=100)
edt_out = Entry(root, width=100)
btn_inp = Button(root, text='...')
btn_out = Button(root, text='...')
btn_start = Button(root, text="запуск")
pb = Progressbar(root, orient='horizontal', mode='indeterminate')

btn_inp.bind("<Button-1>", choose_inp)
btn_out.bind("<Button-1>", choose_out)
btn_start.bind("<Button-1>", start)

edt_inp.grid(row=0, column=1, sticky=W, padx=10)
edt_out.grid(row=1, column=1, sticky=W, padx=10)
btn_inp.grid(row=0, column=2, sticky=E, padx=10)
btn_out.grid(row=1, column=2, sticky=E, padx=10)
pb.grid(row=2, column=0, sticky='W' + 'E', columnspan=3, padx=10, pady=50)
btn_start.place(relx=0.5, rely=0.7, anchor=CENTER, width=100, height=40)

read_conf()

root.mainloop()
