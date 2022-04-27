import queue
import utilities as util
import logging
import pyvisa as vs
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *
import time
import KeysightLib as key


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Keysight App")
        self.geometry('1300x500')
        self.resizable(True, True)

        self.iconbitmap('iconEOTS.ico')

        self.powerread = []
        self.unit = []
        self.range = []
        self.currentrange = []
        self.wav = []
        self.avgtime = []

        self.text_power = []

        self.wav850_btn = []
        self.wav1310_btn = []
        self.wav1490_btn = []
        self.wav1550_btn = []
        self.wav1625_btn = []
        self.avg_btn = []
        self.range_btn = []
        self.W_btn = []
        self.db_btn = []
        self.dbm_btn = []
        self.dark_btn = []
        self.ref_btn = []
        self.start_btn = []
        self.play_btn = []
        self.stop_btn = []

        self.device = StringVar(self, 'test')

        # Layout of window, 1 column per powermeter
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        for p in range(4):
            self.powermeter_frame = self.create_powermeter_frame(p)
            self.powermeter_frame.grid(column=p, row=1, sticky=tk.N, padx=2, pady=8)

        self.setup_frame = self.create_setup_frame()
        self.setup_frame.grid(column=0, row=0, sticky=tk.NSEW, padx=2, pady=8)

    def create_powermeter_frame(self, pownum):
        frame = ttk.LabelFrame(self, text='Powermeter '+str(pownum+1))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=1)
        frame.rowconfigure(0, weight=1)

        self.powerread.append(StringVar(self, '---.---'))
        self.unit.append(StringVar(self, 'dBm'))
        self.range.append(StringVar(self, 'Auto-Range'))
        self.currentrange.append(StringVar(self, '--- dBm'))
        self.wav.append(StringVar(self, '----'))
        self.avgtime.append(StringVar(self, '---'))

        s = ttk.Style()
        s.configure('big.TButton', font=('Calibri', 12))

        text_power = Text(frame, height=1, font='Calibri 35')
        text_power.grid(column=0, row=0, columnspan=5, sticky=tk.NSEW)
        text_power.tag_configure('right', justify='right', foreground='grey')
        text_power.insert(END, self.powerread[pownum].get() + ' ' + self.unit[pownum].get())
        text_power.config(state=DISABLED)
        text_power.tag_add('right', 1.0, END)
        self.text_power.append(text_power)

        ttk.Label(frame, text='Wavelength (nm)', font='Calibri 15').grid(column=0, row=1, columnspan=3, sticky=tk.W)
        wav_entry = ttk.Entry(frame, foreground='grey', font='Calibri 15')
        wav_entry.insert(END, self.wav[pownum].get())
        wav_entry.grid(column=3, row=1, columnspan=2, sticky=tk.W)
        wav_entry.configure(justify=RIGHT)
        wav_entry.bind("<Button-1>", self.on_click)

        wav850_btn = ttk.Button(frame, text='850nm', style='big.TButton', command=lambda: key.wav(pownum, '850'))
        wav850_btn.grid(column=0, row=2)
        wav850_btn['state'] = tk.DISABLED
        self.wav850_btn.append(wav850_btn)
        wav1310_btn = ttk.Button(frame, text='1310nm', style='big.TButton', command=lambda: key.wav(pownum, '1310'))
        wav1310_btn.grid(column=1, row=2)
        wav1310_btn['state'] = tk.DISABLED
        self.wav1310_btn.append(wav1310_btn)
        wav1490_btn = ttk.Button(frame, text='1490nm', style='big.TButton', command=lambda: key.wav(pownum, '1490'))
        wav1490_btn.grid(column=2, row=2)
        wav1490_btn['state'] = tk.DISABLED
        self.wav1490_btn.append(wav1490_btn)
        wav1550_btn = ttk.Button(frame, text='1550nm', style='big.TButton', command=lambda: key.wav(pownum, '1550'))
        wav1550_btn.grid(column=3, row=2)
        wav1550_btn['state'] = tk.DISABLED
        self.wav1550_btn.append(wav1550_btn)
        wav1625_btn = ttk.Button(frame, text='1625nm', style='big.TButton', command=lambda: key.wav(pownum, '1625'))
        wav1625_btn.grid(column=4, row=2)
        wav1625_btn['state'] = tk.DISABLED
        self.wav1625_btn.append(wav1625_btn)

        ttk.Label(frame, text='Avg. Time', font='Calibri 15').grid(column=0, row=3, columnspan=2, sticky=tk.W)
        avg_entry = ttk.Entry(frame, foreground='grey', font='Calibri 15')
        avg_entry.insert(END, self.avgtime[pownum].get())
        avg_entry.grid(column=3, row=3, columnspan=2, sticky=tk.W)
        avg_entry.configure(justify=RIGHT)
        avg_entry.bind("<Button-1>", self.on_click)
        # avg_entry.bind('<Enter>', key.setAvg(pownum, avg_entry.get()))
        avg_btn = ttk.Button(frame, text='\u2261', style='big.TButton', command=lambda: self.avgList(pownum))
        avg_btn.grid(column=2, row=3)
        avg_btn['state'] = tk.DISABLED
        self.avg_btn.append(avg_btn)

        ttk.Label(frame, text=self.range[pownum].get(), font='Calibri 15').grid(column=0, row=4, columnspan=2, sticky=tk.W)
        range_entry = ttk.Entry(frame, foreground='grey', font='Calibri 15')
        range_entry.insert(END, self.currentrange[pownum].get())
        range_entry.grid(column=3, row=4, columnspan=2, sticky=tk.W)
        range_entry.configure(justify=RIGHT)
        range_entry.bind("<Button-1>", self.on_click)
        # range_entry.bind('<Enter>', key.setRange(pownum, range_entry.get()))
        range_btn = ttk.Button(frame, text='\u2261', style='big.TButton', command=lambda: self.rangeList(pownum))
        range_btn.grid(column=2, row=4)
        range_btn['state'] = tk.DISABLED
        self.range_btn.append(range_btn)

        ttk.Label(frame, text='Power Unit', font='Calibri 15').grid(column=0, row=5, columnspan=2, sticky=tk.W)
        W_btn = ttk.Button(frame, text='W', style='big.TButton', command=lambda: key.setUnit(pownum, 'W'))
        W_btn.grid(column=2, row=5, sticky=tk.W + E)
        W_btn['state'] = tk.DISABLED
        self.W_btn.append(W_btn)
        db_btn = ttk.Button(frame, text='dB', style='big.TButton', command=lambda: key.setUnit(pownum, 'dB'))
        db_btn.grid(column=3, row=5, sticky=tk.W + E)
        db_btn['state'] = tk.DISABLED
        self.db_btn.append(db_btn)
        dbm_btn = ttk.Button(frame, text='dBm', style='big.TButton', command=lambda: key.setUnit(pownum, 'dBm'))
        dbm_btn.grid(column=4, row=5, sticky=tk.W + E)
        dbm_btn['state'] = tk.DISABLED
        self.dbm_btn.append(dbm_btn)

        dark_btn = ttk.Button(frame, text='Dark', style='big.TButton', command=lambda: key.dark(pownum))
        dark_btn.grid(column=0, row=6, columnspan=2, sticky=tk.W + E, ipady=10)
        dark_btn['state'] = tk.DISABLED
        self.dark_btn.append(dark_btn)
        ref_btn = ttk.Button(frame, text='Reference', style='big.TButton', command=lambda: key.ref(pownum))
        ref_btn.grid(column=3, row=6, columnspan=2, sticky=tk.W + E, ipady=10)
        ref_btn['state'] = tk.DISABLED
        self.ref_btn.append(ref_btn)

        s = ttk.Style()
        s.configure('big.TButton', font=('Calibri', 12))
        start_btn = ttk.Button(frame, text='Start Live', style='big.TButton', command=lambda: key.live(pownum))
        start_btn.grid(column=0, row=7, columnspan=3, rowspan=2, sticky=tk.NSEW, ipady=15)
        start_btn['state'] = tk.DISABLED
        self.start_btn.append(start_btn)
        play_btn = ttk.Button(frame, text='\u23ef', style='big.TButton', command=lambda: key.live(pownum))
        play_btn.grid(column=3, row=7, rowspan=2, sticky=tk.NSEW, ipady=15)
        play_btn['state'] = tk.DISABLED
        self.play_btn.append(play_btn)
        stop_btn = ttk.Button(frame, text='\u23f9', style='big.TButton', command=lambda: key.live(pownum))
        stop_btn.grid(column=4, row=7, rowspan=2, sticky=tk.NSEW, ipady=15)
        stop_btn['state'] = tk.DISABLED
        self.stop_btn.append(stop_btn)

        for widget in frame.winfo_children():
            widget.grid(padx=1, pady=2)

        return frame

    def create_setup_frame(self):
        frame = ttk.LabelFrame(self, text='Instrument Setup')
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        s = ttk.Style()
        s.configure('bbig.TButton', font=('Calibri', 15))

        ttk.Button(frame, text='Detect Device', style='bbig.TButton', command=lambda: self.setup_device_usb()).grid(column=0, row=0, sticky=tk.EW)
        device_lbl = ttk.Label(frame, textvariable=self.device, font='Calibri 15', justify='center')
        device_lbl.grid(column=1, row=0)





        return frame

    def setup_device(self, device, ip):
        rm = vs.ResourceManager()
        if ip.get() == self.ip_default.get() or not ip.get():
            return None
            pass
        else:
            TCP_INST = "TCPIP::" + ip.get() + "::5025::SOCKET"
            instrument = None
            try:
                instrument = rm.open_resource(TCP_INST, open_timeout=1000)
                instrument.timeout = 10000
                instrument.query_delay = 0
                instrument.write_termination = '\n'
                instrument.read_termination = '\n'
                time.sleep(0.5)
            except Exception as e:
                ip.delete(0, END)
                ip.insert(END, "Failed to open " + device)
                pass
            return instrument

    def setup_device_usb(self):
        rm = vs.ResourceManager()
        instruments = rm.list_resources()
        if any(s.startswith('USB0::0x29CE') for s in instruments):
            r = [s for s in instruments if s.startswith('USB0::0x29CE')]
            for i in r:
                instrument = rm.open_resource(i, open_timeout=5000)
                instrument.timeout = 10000
                instrument.query_delay = 0
                instrument.write_termination = '\n'
                instrument.read_termination = '\n'
                idn = instrument.query('*IDN?')
                idn = idn.split(',')
        return instrument

    def on_click(self, event):
        event.widget.delete(0, tk.END)
        event.widget.unbind('<Button-1>')
        event.widget.config(foreground='black')



if __name__ == "__main__":
    App().mainloop()