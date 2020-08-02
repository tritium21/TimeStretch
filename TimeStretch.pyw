import datetime
from os import path
import re
import sys
import tkinter
from tkinter import ttk


def _parse_time(input_string):
    pat = r'(?:(?:(\d{1,2}):)?(\d{1,2}):)?(\d{1,2})'
    match = re.match(pat, input_string)
    if match is None:
        return 0
    hours, minutes, seconds = match.groups()
    total = int(seconds)
    if minutes:
        total += int(minutes) * 60
    if hours:
        total += int(hours) * 3600
    return total


def _format_time(total_seconds):
    hours, minute_second = divmod(total_seconds, 3600)
    minutes, seconds = divmod(minute_second, 60)
    return "{}:{:0>2}:{:0>2}".format(hours, minutes, seconds)


class Percent(ttk.Frame):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.elapsed = 3600
        self.remaining = 3600
        self.init_vars()
        self.init_ui()

    def init_vars(self):
        self.elapsed_var = tkinter.StringVar()
        self.remaining_var = tkinter.StringVar()
        self.percent_var = tkinter.StringVar()
        self.elapsed_var.trace_add('write', self._trace_elapsed)
        self.remaining_var.trace_add('write', self._trace_remaining)
        self.elapsed_var.set(_format_time(self.elapsed))
        self.remaining_var.set(_format_time(self.remaining))

    def init_ui(self):
        self.grid(column=0, row=0, sticky="NEWS")
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Column 0
        ttk.Label(self, text="Elapsed:").grid(column=0, row=0, sticky="EW")
        ttk.Label(self, text="Remaining:").grid(column=0, row=1, sticky="EW")
        ttk.Label(self, text="Completed:").grid(column=0, row=2, sticky="EW")

        # Column 1
        self.elapsed_input = ttk.Entry(self, textvariable=self.elapsed_var)
        self.elapsed_input.grid(column=1, row=0, sticky="EW")
        self.remaining_input = ttk.Entry(self, textvariable=self.remaining_var)
        self.remaining_input.grid(column=1, row=1, sticky="EW")
        self.percent = ttk.Label(self, textvariable=self.percent_var)
        self.percent.grid(column=1, row=2, sticky="EW")

    def _trace_elapsed(self, *args):
        val = self.elapsed_var.get()
        self.elapsed = _parse_time(val)
        self.update()

    def _trace_remaining(self, *args):
        val = self.remaining_var.get()
        self.remaining = _parse_time(val)
        self.update()

    def update(self):
        total = float(self.elapsed + self.remaining)
        percent = (self.elapsed / total) * 100
        self.percent_var.set("{0:.0f}%".format(percent))


class Stretch(ttk.Frame):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stretch_factor = 1.0
        self.total_seconds = 3600
        self.parent = parent
        self.init_vars()
        self.init_ui()

    def init_vars(self):
        self.input_var = tkinter.StringVar()
        self.output_var = tkinter.StringVar()
        self.stretch_var = tkinter.DoubleVar()
        self.stretch_label_var = tkinter.StringVar()
        self.finish_var = tkinter.StringVar()
        self.input_var.trace_add('write', self._trace_input)
        self.stretch_var.trace_add("write", self._trace_stretch)
        self.input_var.set(_format_time(self.total_seconds))
        self.stretch_var.set(self.stretch_factor)

    def init_ui(self):
        self.grid(column=0, row=0, sticky="NEWS")
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        # Column 0
        ttk.Label(self, text="Duration:").grid(column=0, row=0, sticky="EW")
        ttk.Label(self, text="Scale:").grid(column=0, row=1, sticky="EW")
        ttk.Label(self, text="Remaining:").grid(column=0, row=2, sticky="EW")
        ttk.Label(self, text="Finished at:").grid(column=0, row=3, sticky="EW")

        # Column 1
        self.input = ttk.Entry(self, textvariable=self.input_var)
        self.input.grid(column=1, row=0, sticky="EW", columnspan=2)
        self.stretch = ttk.Scale(self, from_=0.1, to=3.0, variable=self.stretch_var)
        self.stretch.grid(column=1, row=1, sticky="EW")
        self.output = ttk.Label(self, textvariable=self.output_var)
        self.output.grid(column=1, row=2, sticky="EW", columnspan=2)
        self.finish = ttk.Label(self, textvariable=self.finish_var)
        self.finish.grid(column=1, row=3, sticky="EW", columnspan=2)

        # Column 2
        self.stretch_label = ttk.Label(self, textvariable=self.stretch_label_var)
        self.stretch_label.grid(column=2, row=1, sticky="EW")

    def _trace_stretch(self, *args):
        val = self.stretch_var.get()
        self.stretch_factor = round(val, 1)
        self.stretch_label_var.set("{}x".format(self.stretch_factor))
        self.update()

    def _trace_input(self, *args):
        val = self.input_var.get()
        self.total_seconds = _parse_time(val)
        self.update()

    def update(self):
        out = int(self.total_seconds / self.stretch_factor)
        self.output_var.set(_format_time(out))
        td = datetime.timedelta(seconds=out)
        finish = datetime.datetime.now() + td
        self.finish_var.set(finish.strftime('%x %X'))


class App:
    def __init__(self, root=None):
        if root is None:
            self.root = tkinter.Tk()
            self.init_root()
        else:
            self.root = root
        self.init_ui()

    def init_root(self):
        self.root.columnconfigure(0, weight=1)
        self.root.resizable(0, 0)
        self.root.minsize(width=300, height=0)
        self.root.title("Time Stretch Calculator")
        self.init_icon()

    def init_icon(self):
        if getattr(sys, 'frozen', False):
            icon = path.join(sys._MEIPASS, 'clock.ico')
        else:
            icon = path.join(path.dirname(path.abspath(__file__)), 'clock.ico')
        self.root.iconbitmap(icon)

    def init_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(column=0, row=0, sticky="NEWS")
        self.notebook.add(Stretch(self.root), text="Stretch")
        self.notebook.add(Percent(self.root), text="Completion")

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    App().mainloop()
