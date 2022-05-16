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
from threading import Thread
from queue import Queue


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Keysight App")
        self.geometry('1300x535')
        self.resizable(True, True)

        self.iconbitmap('iconEOTS.ico')

        self.powerread = []
        self.unit = []
        self.range = []
        self.currentrange = []
        self.wav = []
        self.avgtime = []

        self.lbl_power = []

        self.wav850_btn = []
        self.wav1310_btn = []
        self.wav1490_btn = []
        self.wav1550_btn = []
        self.wav1625_btn = []
        self.wav_entry = []
        self.avg_btn = []
        self.avg_entry = []
        self.range_btn = []
        self.range_entry = []
        self.W_btn = []
        self.db_btn = []
        self.dbm_btn = []
        self.dark_btn = []
        self.ref_btn = []
        self.start_btn = []
        self.play_btn = []
        self.stop_btn = []
        self.params = [
            {'wavelength': '', 'average': '', 'range': '', 'unit': ''},
            {'wavelength': '', 'average': '', 'range': '', 'unit': ''},
            {'wavelength': '', 'average': '', 'range': '', 'unit': ''},
            {'wavelength': '', 'average': '', 'range': '', 'unit': ''}
        ]

        self.device = StringVar()
        self.deviceip = StringVar()

        self.device_lbl = None
        self.deviceip_lbl = None

        self.instrument = None
        self.instrumentip = None

        self.avglist = None
        self.rangelist = None

        self.live_thread = None
        self.state = [False, False, False, False]
        self.pow_queue = Queue()
        self.stat_queue = Queue()
        self.except_queue = Queue()
        self.params_queue = Queue()

        # Layout of window, 1 column per powermeter
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        for p in range(4):
            self.powermeter_frame = self.create_powermeter_frame(p)
            self.powermeter_frame.grid(column=p, row=1, sticky=tk.N, padx=2)

        self.setup_frame = self.create_setup_frame()
        self.setup_frame.grid(column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=2, pady=8)

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
        self.range.append(StringVar(self, 'Auto Range'))
        self.currentrange.append(StringVar(self, 'Auto'))
        self.wav.append(StringVar(self, '----'))
        self.avgtime.append(StringVar(self, '---'))

        s = ttk.Style()
        s.configure('big.TButton', font=('Calibri', 12))

        # Power reading box
        lbl_power = ttk.Label(frame, textvariable=self.powerread[pownum], font='Calibri 35', foreground='grey', background='white', justify=RIGHT)
        lbl_power.grid(column=0, row=0, columnspan=4, sticky=tk.NSEW)
        ttk.Label(frame, textvariable=self.unit[pownum], font='Calibri 25', foreground='black').grid(column=4, row=0, sticky=tk.NSEW)
        self.lbl_power.append(lbl_power)

        # Wavelength Entry
        ttk.Label(frame, text='Wavelength (nm)', font='Calibri 15').grid(column=0, row=1, columnspan=3, sticky=tk.W)
        wav_entry = ttk.Entry(frame, foreground='grey', font='Calibri 15')
        wav_entry.insert(END, self.wav[pownum].get())
        wav_entry.grid(column=3, row=1, columnspan=2, sticky=tk.W)
        wav_entry.configure(justify=RIGHT)
        wav_entry.bind("<Button-1>", self.on_click)
        wav_entry.bind('<Return>', lambda event: self.setwav(pownum, wav_entry.get()))
        self.wav_entry.append(wav_entry)

        # Preset wavelength buttons
        wav850_btn = ttk.Button(frame, text='850nm', style='big.TButton', command=lambda: self.setwav(pownum, '850'))
        wav850_btn.grid(column=0, row=2)
        wav850_btn['state'] = tk.DISABLED
        self.wav850_btn.append(wav850_btn)
        wav1310_btn = ttk.Button(frame, text='1310nm', style='big.TButton', command=lambda: self.setwav(pownum, '1310'))
        wav1310_btn.grid(column=1, row=2)
        wav1310_btn['state'] = tk.DISABLED
        self.wav1310_btn.append(wav1310_btn)
        wav1490_btn = ttk.Button(frame, text='1490nm', style='big.TButton', command=lambda: self.setwav(pownum, '1490'))
        wav1490_btn.grid(column=2, row=2)
        wav1490_btn['state'] = tk.DISABLED
        self.wav1490_btn.append(wav1490_btn)
        wav1550_btn = ttk.Button(frame, text='1550nm', style='big.TButton', command=lambda: self.setwav(pownum, '1550'))
        wav1550_btn.grid(column=3, row=2)
        wav1550_btn['state'] = tk.DISABLED
        self.wav1550_btn.append(wav1550_btn)
        wav1625_btn = ttk.Button(frame, text='1625nm', style='big.TButton', command=lambda: self.setwav(pownum, '1625'))
        wav1625_btn.grid(column=4, row=2)
        wav1625_btn['state'] = tk.DISABLED
        self.wav1625_btn.append(wav1625_btn)

        # Averaging Time Entry and Browse button
        ttk.Label(frame, text='Avg. Time', font='Calibri 15').grid(column=0, row=3, columnspan=2, sticky=tk.W)
        avg_entry = ttk.Entry(frame, foreground='grey', font='Calibri 15')
        avg_entry.insert(END, self.avgtime[pownum].get())
        avg_entry.grid(column=3, row=3, columnspan=2, sticky=tk.W)
        avg_entry.configure(justify=RIGHT)
        avg_entry.bind("<Button-1>", self.on_click)
        avg_entry.bind('<Return>', lambda event: self.closeavg(pownum))
        self.avg_entry.append(avg_entry)
        avg_btn = ttk.Button(frame, text='\u2261', style='big.TButton', command=lambda: self.avgwindow(pownum))
        avg_btn.grid(column=2, row=3)
        avg_btn['state'] = tk.DISABLED
        self.avg_btn.append(avg_btn)

        # Gain Range Entry and browse button
        ttk.Label(frame, textvariable=self.range[pownum], font='Calibri 15').grid(column=0, row=4, columnspan=2, sticky=tk.W)
        range_entry = ttk.Entry(frame, foreground='grey', font='Calibri 15')
        range_entry.insert(END, self.currentrange[pownum].get())
        range_entry.grid(column=3, row=4, columnspan=2, sticky=tk.W)
        range_entry.configure(justify=RIGHT)
        range_entry.bind("<Button-1>", self.on_click)
        range_entry.bind('<Return>', lambda event: self.closerange(pownum))
        self.range_entry.append(range_entry)
        range_btn = ttk.Button(frame, text='\u2261', style='big.TButton', command=lambda: self.rangewindow(pownum))
        range_btn.grid(column=2, row=4)
        range_btn['state'] = tk.DISABLED
        self.range_btn.append(range_btn)

        # Power Unit buttons
        ttk.Label(frame, text='Power Unit', font='Calibri 15').grid(column=0, row=5, columnspan=2, sticky=tk.W)
        W_btn = ttk.Button(frame, text='W', style='big.TButton', command=lambda: self.setunit(pownum, 'mW'))
        W_btn.grid(column=3, row=5, sticky=tk.W + E)
        W_btn['state'] = tk.DISABLED
        self.W_btn.append(W_btn)
        # db_btn = ttk.Button(frame, text='dB', style='big.TButton', command=lambda: self.setunit(pownum, 'dB'))
        # db_btn.grid(column=3, row=5, sticky=tk.W + E)
        # db_btn['state'] = tk.DISABLED
        # self.db_btn.append(db_btn)
        dbm_btn = ttk.Button(frame, text='dBm', style='big.TButton', command=lambda: self.setunit(pownum, 'dBm'))
        dbm_btn.grid(column=4, row=5, sticky=tk.W + E)
        dbm_btn['state'] = tk.DISABLED
        self.dbm_btn.append(dbm_btn)

        # Dark button
        dark_btn = ttk.Button(frame, text='Dark', style='big.TButton', command=lambda: self.dark(pownum))
        dark_btn.grid(column=0, row=6, columnspan=2, sticky=tk.W + E, ipady=10)
        dark_btn['state'] = tk.DISABLED
        self.dark_btn.append(dark_btn)

        # Reference button
        ref_btn = ttk.Button(frame, text='Reference', style='big.TButton', command=lambda: self.ref(pownum))
        ref_btn.grid(column=3, row=6, columnspan=2, sticky=tk.W + E, ipady=10)
        ref_btn['state'] = tk.DISABLED
        self.ref_btn.append(ref_btn)

        # Start Live reading, Play/Pause and Stop buttons
        s = ttk.Style()
        s.configure('big.TButton', font=('Calibri', 12))
        start_btn = ttk.Button(frame, text='Start Live', style='big.TButton', command=lambda: self.start(pownum))
        start_btn.grid(column=0, row=7, columnspan=3, rowspan=2, sticky=tk.NSEW, ipady=15)
        start_btn['state'] = tk.DISABLED
        self.start_btn.append(start_btn)
        play_btn = ttk.Button(frame, text='\u23ef', style='big.TButton', command=lambda: self.pauseplay(pownum))
        play_btn.grid(column=3, row=7, rowspan=2, sticky=tk.NSEW, ipady=15)
        play_btn['state'] = tk.DISABLED
        self.play_btn.append(play_btn)
        stop_btn = ttk.Button(frame, text='\u23f9', style='big.TButton', command=lambda: self.stop(pownum))
        stop_btn.grid(column=4, row=7, rowspan=2, sticky=tk.NSEW, ipady=15)
        stop_btn['state'] = tk.DISABLED
        self.stop_btn.append(stop_btn)

        for widget in frame.winfo_children():
            widget.grid(padx=1, pady=2)

        return frame

    def create_setup_frame(self):
        # Instrument setup (USB and Ethernet connection)
        frame = ttk.LabelFrame(self, text='Instrument Setup')
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        s = ttk.Style()
        s.configure('bbig.TButton', font=('Calibri', 15))

        # USB connection button and result
        ttk.Button(frame, text='Detect USB Device', style='bbig.TButton', width=20, command=lambda: self.setup_device_usb()).grid(column=0, row=0, sticky=tk.EW)
        self.device_lbl = ttk.Label(frame, textvariable=self.device, font='Calibri 15', justify='center')
        self.device_lbl.grid(column=0, row=1)

        # Ethernet connection button and result
        ip_entry = ttk.Entry(frame, foreground='grey', width=20, font='Calibri 15', justify='center')
        ip_entry.insert(END, 'xxx.xxx.xx.xxx')
        ip_entry.grid(column=1, row=0, sticky=tk.EW)
        ip_entry.bind("<Button-1>", self.on_click)
        ip_entry.bind('<Return>', lambda event: self.setup_device(ip_entry))
        self.deviceip_lbl = ttk.Label(frame, textvariable=self.deviceip, font='Calibri 15', justify='center')
        self.deviceip_lbl.grid(column=1, row=1)
        ttk.Button(frame, text='Test Connection', style='bbig.TButton', width=20, command=lambda: self.setup_device(ip_entry)).grid(column=2, row=0, sticky=tk.EW)

        for widget in frame.winfo_children():
            widget.grid(padx=1, pady=2)

        return frame

    def setup_device(self, ip):
        rm = vs.ResourceManager()
        if ip.get() == 'xxx.xxx.xx.xxx' or not ip.get():
            self.deviceip.set('No IP address')
            self.deviceip_lbl.configure(foreground='red')
            self.instrumentip = None
            if self.instrument is None:
                for p in range(4):
                    self.start_btn[p]['state'] = tk.DISABLED
            pass
        else:
            TCP_INST = "TCPIP::" + ip.get() + "::5025::SOCKET"
            try:
                instrument = rm.open_resource(TCP_INST, open_timeout=1000)
                instrument.timeout = 10000
                instrument.query_delay = 0
                instrument.write_termination = '\n'
                instrument.read_termination = '\n'
                time.sleep(0.5)
                self.instrumentip = instrument
                self.deviceip.set('Connected to N7744A')
                self.deviceip_lbl.configure(foreground='green')
                ip.bind("<Button-1>", self.on_click)
                for p in range(4):
                    self.start_btn[p]['state'] = tk.NORMAL
            except Exception as e:
                self.deviceip.set('Failed to open')
                self.deviceip_lbl.configure(foreground='red')
                self.instrumentip = None
                for p in range(4):
                    self.start_btn[p]['state'] = tk.DISABLED
                pass

    def setup_device_usb(self):
        rm = vs.ResourceManager()
        instruments = rm.list_resources()
        if any(s.startswith('USB0::0x0957') for s in instruments):
            r = [s for s in instruments if s.startswith('USB0::0x0957')]
            try:
                for i in r:
                    instrument = rm.open_resource(i, open_timeout=5000)
                    instrument.timeout = 10000
                    instrument.query_delay = 0
                    instrument.write_termination = '\n'
                    instrument.read_termination = '\n'
                    idn = instrument.query('*IDN?')
                    idn = idn.split(',')
                    if idn[1] == ' N7744A':
                        self.device.set('Connected to N7744A')
                        self.device_lbl.configure(foreground='green')
                        self.instrument = instrument
                        for p in range(4):
                            self.start_btn[p]['state'] = tk.NORMAL
            except Exception as e:
                self.device.set('Failed to open')
                self.device_lbl.configure(foreground='red')
                self.instrument = None
                if self.instrumentip is None:
                    for p in range(4):
                        self.start_btn[p]['state'] = tk.DISABLED
                pass
        else:
            self.device.set('No instrument connected')
            self.device_lbl.configure(foreground='red')
            self.instrument = None
            if self.instrumentip is None:
                for p in range(4):
                    self.start_btn[p]['state'] = tk.DISABLED

    def on_click(self, event):
        event.widget.delete(0, tk.END)
        event.widget.unbind('<Button-1>')
        event.widget.config(foreground='black')

    def avgwindow(self, pnum):
        avglistwin = tk.Tk()
        avglistwin.wm_title('Avg Time PM ' + str(pnum+1))
        avglistwin.geometry('250x460')
        avglistwin.resizable(True, True)
        avglistwin.iconbitmap('iconEOTS.ico')

        frame = ttk.Frame(avglistwin)
        frame.grid(column=0, row=0)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        avgval = (
            '1 us',
            '10 us',
            '20 s',
            '50 us',
            '100 us',
            '200 us',
            '500 us',
            '1 ms',
            '10 ms',
            '20 ms',
            '50 ms',
            '100 ms',
            '200 ms',
            '500 ms',
            '1 s',
            '2 s',
            '5 s',
            '10 s'
        )

        avgval_var = StringVar(avglistwin, value=avgval)

        self.avglist = Listbox(frame, listvariable=avgval_var, width=15, height=18, justify='center', selectmode='single', font='Calibri 15')
        self.avglist.grid(column=0, row=0, columnspan=2, rowspan=18, sticky=tk.NSEW)

        w = ttk.Style()
        w.configure('bbbig.TButton', font=('Calibri', 15))
        ttk.Button(frame, text='Ok', width=12, style='bbbig.TButton', command=lambda: self.closeavg(pnum, avglistwin)).grid(column=2, row=0, sticky=tk.E, padx=6, pady=2)
        ttk.Button(frame, text='Cancel', width=12, style='bbbig.TButton', command=lambda: self.cancel(avglistwin)).grid(column=2, row=1, sticky=tk.E, padx=6, pady=2)

    def rangewindow(self, pnum):
        rangelistwin = tk.Tk()
        rangelistwin.wm_title('Gain Range PM ' + str(pnum+1))
        rangelistwin.geometry('250x235')
        rangelistwin.resizable(True, True)
        rangelistwin.iconbitmap('iconEOTS.ico')

        frame = ttk.Frame(rangelistwin)
        frame.grid(column=0, row=0)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        rangeval = (
            'Auto Range',
            '+10 dBm',
            '0 dBm',
            '-10 dBm',
            '-20 dBm',
            '-30 dBm',
            '-40 dBm',
            '-50 dBm',
            '-60 dBm'
        )

        rangeval_var = StringVar(rangelistwin, value=rangeval)

        self.rangelist = Listbox(frame, listvariable=rangeval_var, width=15, height=9, justify='center', selectmode='single', font='Calibri 15')
        self.rangelist.grid(column=0, row=0, columnspan=2, rowspan=9, sticky=tk.NSEW)

        z = ttk.Style()
        z.configure('bbbig.TButton', font=('Calibri', 15))
        ttk.Button(frame, text='Ok', width=12, style='bbbig.TButton', command=lambda: self.closerange(pnum, rangelistwin)).grid(column=2, row=0, sticky=tk.E, padx=6, pady=2)
        ttk.Button(frame, text='Cancel', width=12, style='bbbig.TButton', command=lambda: self.cancel(rangelistwin)).grid(column=2, row=1, sticky=tk.E, padx=6, pady=2)

    def closeavg(self, pnum, win=None):
        if win is not None:
            self.avg_entry[pnum].delete(0, END)
            self.avg_entry[pnum].insert(0, self.avglist.get(self.avglist.curselection()))
            self.avg_entry[pnum].bind("<Button-1>", self.on_click)
            self.avg_entry[pnum].bind('<Return>', lambda event: self.closeavg(pnum))
            self.params[pnum]['average'] = self.avg_entry[pnum].get().replace(' ', '')
            self.params_queue.put_nowait([self.params[pnum], pnum])
            win.destroy()
        else:
            self.avg_entry[pnum].bind("<Button-1>", self.on_click)
            self.avg_entry[pnum].bind('<Return>', lambda event: self.closeavg(pnum))
            self.params[pnum]['average'] = self.avg_entry[pnum].get().replace(' ', '')
            self.params_queue.put_nowait([self.params[pnum], pnum])

    def closerange(self, pnum, win=None):
        if win is not None:
            self.range_entry[pnum].delete(0, END)
            if self.rangelist.get(self.rangelist.curselection()) == 'Auto Range':
                self.range_entry[pnum].insert(0, 'Auto')
                self.range_entry[pnum].configure(foreground='grey')
                self.range[pnum].set('Auto Range')
                self.range_entry[pnum].bind("<Button-1>", self.on_click)
                self.range_entry[pnum].bind('<Return>', lambda event: self.closerange(pnum))
                self.params[pnum]['range'] = self.range_entry[pnum].get()
                self.params_queue.put_nowait([self.params[pnum], pnum])
            else:
                self.range_entry[pnum].insert(0, self.rangelist.get(self.rangelist.curselection()))
                self.range_entry[pnum].configure(foreground='black')
                self.range[pnum].set('Manual Range')
                self.range_entry[pnum].bind("<Button-1>", self.on_click)
                self.range_entry[pnum].bind('<Return>', lambda event: self.closerange(pnum))
                self.params[pnum]['range'] = self.range_entry[pnum].get().replace(' ', '')
                self.params_queue.put_nowait([self.params[pnum], pnum])
            win.destroy()
        else:
            if self.range_entry[pnum].get() == 'Auto-Range' or self.range_entry[pnum].get() == 'Auto':
                self.range_entry[pnum].configure(foreground='grey')
                self.range[pnum].set('Auto Range')
                self.range_entry[pnum].bind("<Button-1>", self.on_click)
                self.range_entry[pnum].bind('<Return>', lambda event: self.closerange(pnum))
                self.params[pnum]['range'] = self.range_entry[pnum].get()
                self.params_queue.put_nowait([self.params[pnum], pnum])
            else:
                self.range[pnum].set('Manual Range')
                self.range_entry[pnum].configure(foreground='black')
                self.range_entry[pnum].bind("<Button-1>", self.on_click)
                self.range_entry[pnum].bind('<Return>', lambda event: self.closerange(pnum))
                self.params[pnum]['range'] = self.range_entry[pnum].get().replace(' ', '')
                self.params_queue.put_nowait([self.params[pnum], pnum])

    def cancel(self, win):
        win.destroy()

    def setunit(self, pnum, unit):
        self.unit[pnum].set(unit)
        self.params[pnum]['unit'] = unit
        self.params_queue.put_nowait([self.params[pnum], pnum])

    def setwav(self, pnum, wav):
        self.wav[pnum].set(wav)
        self.wav_entry[pnum].delete(0, END)
        self.wav_entry[pnum].insert(0, self.wav[pnum].get())
        self.wav_entry[pnum].bind("<Button-1>", self.on_click)
        self.wav_entry[pnum].bind('<Return>', lambda event: self.setwav(pnum, self.wav_entry[pnum].get()))
        self.params[pnum]['wavelength'] = wav
        self.params_queue.put_nowait([self.params[pnum], pnum])

    def setatime(self, pnum, atime):
        atime.replace(' ', '')
        self.avgtime[pnum].set(atime)
        self.avg_entry[pnum].delete(0, END)
        self.avg_entry[pnum].insert(0, self.avgtime[pnum].get())
        self.avg_entry[pnum].bind("<Button-1>", self.on_click)
        self.avg_entry[pnum].bind('<Return>', lambda event: self.setatime(pnum, self.avg_entry[pnum].get()))
        self.params[pnum]['average'] = atime
        self.params_queue.put_nowait([self.params[pnum], pnum])

    def dark(self, pnum):
        self.wav850_btn[pnum]['state'] = tk.DISABLED
        self.wav1310_btn[pnum]['state'] = tk.DISABLED
        self.wav1490_btn[pnum]['state'] = tk.DISABLED
        self.wav1550_btn[pnum]['state'] = tk.DISABLED
        self.wav1625_btn[pnum]['state'] = tk.DISABLED
        self.avg_btn[pnum]['state'] = tk.DISABLED
        self.range_btn[pnum]['state'] = tk.DISABLED
        self.W_btn[pnum]['state'] = tk.DISABLED
        self.dbm_btn[pnum]['state'] = tk.DISABLED
        self.dark_btn[pnum]['state'] = tk.DISABLED
        self.ref_btn[pnum]['state'] = tk.DISABLED
        self.stop_btn[pnum]['state'] = tk.DISABLED
        self.play_btn[pnum]['state'] = tk.DISABLED
        if self.instrument is not None:
            device = self.instrument
        else:
            device = self.instrumentip
        if self.state[pnum]:
            self.pauseplay(pnum)
            self.powerread[pnum].set('Darking..')
            key.dark(device, pnum)
            self.pauseplay(pnum)
        else:
            self.powerread[pnum].set('Darking..')
            key.dark(device, pnum)
        self.wav850_btn[pnum]['state'] = tk.DISABLED
        self.wav1310_btn[pnum]['state'] = tk.NORMAL
        self.wav1490_btn[pnum]['state'] = tk.NORMAL
        self.wav1550_btn[pnum]['state'] = tk.NORMAL
        self.wav1625_btn[pnum]['state'] = tk.NORMAL
        self.avg_btn[pnum]['state'] = tk.NORMAL
        self.range_btn[pnum]['state'] = tk.NORMAL
        self.W_btn[pnum]['state'] = tk.NORMAL
        self.dbm_btn[pnum]['state'] = tk.NORMAL
        self.dark_btn[pnum]['state'] = tk.NORMAL
        self.ref_btn[pnum]['state'] = tk.NORMAL
        self.stop_btn[pnum]['state'] = tk.NORMAL
        self.play_btn[pnum]['state'] = tk.NORMAL

    def monitor(self, thread):
        if thread.is_alive() and any(self.state):
            try:
                e = self.except_queue.get_nowait()
                self.device.set(str(e))
                self.device_lbl.configure(foreground='red')
                pass
            except queue.Empty:
                pass
            try:
                power = self.pow_queue.get_nowait()
                for p in range(4):
                    if self.state[p]:
                        self.powerread[p].set(str(round(power[p], 3)))
                self.after(25, lambda: self.monitor(thread))
            except queue.Empty:
                self.after(25, lambda: self.monitor(thread))
        else:
          pass

    def start(self, pnum):
        self.wav850_btn[pnum]['state'] = tk.DISABLED
        self.wav1310_btn[pnum]['state'] = tk.NORMAL
        self.wav1490_btn[pnum]['state'] = tk.NORMAL
        self.wav1550_btn[pnum]['state'] = tk.NORMAL
        self.wav1625_btn[pnum]['state'] = tk.NORMAL
        self.avg_btn[pnum]['state'] = tk.NORMAL
        self.range_btn[pnum]['state'] = tk.NORMAL
        self.W_btn[pnum]['state'] = tk.NORMAL
        self.dbm_btn[pnum]['state'] = tk.NORMAL
        self.dark_btn[pnum]['state'] = tk.NORMAL
        self.ref_btn[pnum]['state'] = tk.NORMAL
        self.start_btn[pnum]['state'] = tk.DISABLED
        self.stop_btn[pnum]['state'] = tk.NORMAL
        self.play_btn[pnum]['state'] = tk.NORMAL
        self.state[pnum] = True
        if self.live_thread is not None:
            pass
        else:
            if self.instrument is not None:
                device = self.instrument
            else:
                device = self.instrumentip
            for p in range(4):
                # self.setwav(p, '1550')
                self.params[p]['wavelength'] = '1550'
                # self.setunit(p, 'dBm')
                self.params[p]['unit'] = 'dBm'
                # self.setatime(p, '1ms')
                self.params[p]['average'] = '1ms'
                # self.closerange(p)
                self.params[p]['range'] = 'Auto'
            # self.params_queue.put_nowait(self.params)
            self.live_thread = Live(device, self.state, self.params, self.stat_queue, self.pow_queue, self.except_queue, self.params_queue)
            self.live_thread.start()
            self.monitor(self.live_thread)

    def pauseplay(self, pnum):
        if not any(self.state):
            self.state[pnum] = not self.state[pnum]
            self.stat_queue.put(self.state)
            if self.instrument is not None:
                device = self.instrument
            else:
                device = self.instrumentip
            while not self.pow_queue.empty():
                try:
                    self.pow_queue.get(False)
                except queue.Empty:
                    continue
                self.pow_queue.task_done()
            self.live_thread = Live(device, self.state, self.params, self.stat_queue, self.pow_queue, self.except_queue, self.params_queue)
            self.live_thread.start()
            self.monitor(self.live_thread)
        else:
            self.state[pnum] = not self.state[pnum]


class Live(Thread):
    def __init__(self, device, state, params, stat_queue, pow_queue, except_queue, params_queue):
        super().__init__()
        self.device = device
        self.state = state
        self.params = params
        self.stat_queue = stat_queue
        self.pow_queue = pow_queue
        self.except_queue = except_queue
        self.params_queue = params_queue
        self.status = [str(i) for i in self.state]

    def run(self):
        for p in range(4):
            key.conttrig(self.device, p, 1)
            key.setwav(self.device, p, self.params[p]['wavelength'])
            key.setatime(self.device, p, self.params[p]['average'])
            key.setrange(self.device, p, self.params[p]['range'])
            key.setunit(self.device, p, self.params[p]['unit'])
        while 'True' in self.status:
            try:
                stat = self.stat_queue.get_nowait()
                self.status = [str(i) for i in stat]
            except queue.Empty:
                pass
            try:
                para = self.params_queue.get_nowait()
                key.setwav(self.device, para[1], para[0]['wavelength'])
                key.setatime(self.device, para[1], para[0]['average'])
                key.setrange(self.device, para[1], para[0]['range'])
                key.setunit(self.device, para[1], para[0]['unit'])
            except queue.Empty:
                pass
            try:
                time.sleep(0.1)
                readpow = key.readpow(self.device)
                self.pow_queue.put_nowait(readpow)
            except Exception as e:
                self.except_queue.put('N7744A timed out')
                self.state = False


if __name__ == "__main__":
    App().mainloop()
