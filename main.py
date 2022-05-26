import queue
import pyvisa as vs
import tkinter as tk
from tkinter import ttk
from tkinter import *
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

        self.darkall_btn = None
        self.ip_btn = None
        self.ip_entry = None
        self.stop_btn = None

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
        self.params = [
            {'wavelength': '1550', 'average': '100ms', 'range': 'Auto', 'unit': 'dBm', 'mode': 0},
            {'wavelength': '1550', 'average': '100ms', 'range': 'Auto', 'unit': 'dBm', 'mode': 0},
            {'wavelength': '1550', 'average': '100ms', 'range': 'Auto', 'unit': 'dBm', 'mode': 0},
            {'wavelength': '1550', 'average': '100ms', 'range': 'Auto', 'unit': 'dBm', 'mode': 0}
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
        self.dark_thread = None
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
        self.setup_device_usb()
        # if self.instrument is not None:
        #     self.getip(self.instrument)

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
        wav850_btn = ttk.Button(frame, text='850', style='big.TButton', command=lambda: self.setwav(pownum, '850'))
        wav850_btn.grid(column=0, row=2)
        wav850_btn['state'] = tk.DISABLED
        self.wav850_btn.append(wav850_btn)
        wav1310_btn = ttk.Button(frame, text='1310', style='big.TButton', command=lambda: self.setwav(pownum, '1310'))
        wav1310_btn.grid(column=1, row=2)
        wav1310_btn['state'] = tk.DISABLED
        self.wav1310_btn.append(wav1310_btn)
        wav1490_btn = ttk.Button(frame, text='1490', style='big.TButton', command=lambda: self.setwav(pownum, '1490'))
        wav1490_btn.grid(column=2, row=2)
        wav1490_btn['state'] = tk.DISABLED
        self.wav1490_btn.append(wav1490_btn)
        wav1550_btn = ttk.Button(frame, text='1550', style='big.TButton', command=lambda: self.setwav(pownum, '1550'))
        wav1550_btn.grid(column=3, row=2)
        wav1550_btn['state'] = tk.DISABLED
        self.wav1550_btn.append(wav1550_btn)
        wav1625_btn = ttk.Button(frame, text='1625', style='big.TButton', command=lambda: self.setwav(pownum, '1625'))
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
        W_btn.grid(column=2, row=5, sticky=tk.W + E)
        W_btn['state'] = tk.DISABLED
        self.W_btn.append(W_btn)
        dbm_btn = ttk.Button(frame, text='dBm', style='big.TButton', command=lambda: self.setunit(pownum, 'dBm'))
        dbm_btn.grid(column=3, row=5, sticky=tk.W + E)
        dbm_btn['state'] = tk.DISABLED
        self.dbm_btn.append(dbm_btn)
        db_btn = ttk.Button(frame, text='dB', style='big.TButton', command=lambda: self.setunit(pownum, 'dB', True))
        db_btn.grid(column=4, row=5, sticky=tk.W + E)
        db_btn['state'] = tk.DISABLED
        self.db_btn.append(db_btn)

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
        start_btn.grid(column=0, row=7, columnspan=2, rowspan=2, sticky=tk.NSEW, ipady=15)
        start_btn['state'] = tk.DISABLED
        self.start_btn.append(start_btn)
        play_btn = ttk.Button(frame, text='\u23ef', style='big.TButton', command=lambda: self.pauseplay(pownum))
        play_btn.grid(column=3, row=7, columnspan=2, rowspan=2, sticky=tk.NSEW, ipady=15)
        play_btn['state'] = tk.DISABLED
        self.play_btn.append(play_btn)

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

        #Get ip address button
        self.ip_btn = ttk.Button(frame, text='Get IP address', style='bbig.TButton', width=20, command=lambda: self.getip(self.instrument))
        self.ip_btn.grid(column=0, row=2, sticky=tk.EW)
        self.ip_btn['state'] = tk.DISABLED

        # Ethernet connection button and result
        self.ip_entry = ttk.Entry(frame, foreground='grey', width=20, font='Calibri 15', justify='center')
        self.ip_entry.insert(END, '192.168.12.94')
        self.ip_entry.grid(column=1, row=0, sticky=tk.EW)
        self.ip_entry.bind("<Button-1>", self.on_click)
        self.ip_entry.bind('<Return>', lambda event: self.setup_device(self.ip_entry))
        self.deviceip_lbl = ttk.Label(frame, textvariable=self.deviceip, font='Calibri 15', justify='center')
        self.deviceip_lbl.grid(column=1, row=1)
        ttk.Button(frame, text='Test Connection', style='bbig.TButton', width=20, command=lambda: self.setup_device(self.ip_entry)).grid(column=2, row=0, sticky=tk.EW)
        self.darkall_btn = ttk.Button(frame, text='Dark All PM', style='bbig.TButton', width=20, command=lambda: self.dark('All'))
        self.darkall_btn.grid(column=2, row=1, sticky=tk.EW)
        self.darkall_btn['state'] = tk.DISABLED

        # Stop button to kill thread
        self.stop_btn = ttk.Button(frame, text='Stop Live reading', style='bbig.TButton', width=20, command=lambda: self.stop())
        self.stop_btn.grid(column=2, row=2, sticky=tk.EW)
        self.stop_btn['state'] = tk.DISABLED

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
                ip.config(foreground='black')
                ip.bind("<Button-1>", self.on_click)
                for p in range(4):
                    self.start_btn[p]['state'] = tk.NORMAL
                self.darkall_btn['state'] = tk.NORMAL
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
                        self.darkall_btn['state'] = tk.NORMAL
                        self.ip_btn['state'] = tk.NORMAL
            except Exception as e:
                self.device.set('Failed to open')
                self.device_lbl.configure(foreground='red')
                self.instrument = None
                if self.instrumentip is None:
                    for p in range(4):
                        self.start_btn[p]['state'] = tk.DISABLED
                pass
        else:
            self.device.set('No USB instrument')
            self.device_lbl.configure(foreground='black')
            self.instrument = None
            if self.instrumentip is None:
                for p in range(4):
                    self.start_btn[p]['state'] = tk.DISABLED

    def getip(self, device):
        ip = key.getip(device)
        if ip.startswith('192'):
            self.ip_entry.delete(0, END)
            self.ip_entry.insert(END, ip)
            self.ip_entry.configure(foreground='black')
            self.ip_entry.bind("<Button-1>", self.on_click)
            self.ip_entry.bind('<Return>', lambda event: self.setup_device(self.ip_entry))
        else:
            self.deviceip.set(ip)
            self.deviceip_lbl.configure(foreground='red')

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
            self.avg_entry[pnum].configure(foreground='black')
            self.avg_entry[pnum].bind("<Button-1>", self.on_click)
            self.avg_entry[pnum].bind('<Return>', lambda event: self.closeavg(pnum))
            self.params[pnum]['average'] = self.avg_entry[pnum].get().replace(' ', '')
            if self.params[pnum]['mode'] != 0:
                self.params[pnum]['mode'] = 1
            self.params_queue.put_nowait([self.params[pnum], pnum])
            win.destroy()
        else:
            self.avg_entry[pnum].bind("<Button-1>", self.on_click)
            self.avg_entry[pnum].bind('<Return>', lambda event: self.closeavg(pnum))
            self.params[pnum]['average'] = self.avg_entry[pnum].get().replace(' ', '')
            if self.params[pnum]['mode'] != 0:
                self.params[pnum]['mode'] = 1
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
                if self.params[pnum]['mode'] != 0:
                    self.params[pnum]['mode'] = 1
                self.params_queue.put_nowait([self.params[pnum], pnum])
            else:
                self.range_entry[pnum].insert(0, self.rangelist.get(self.rangelist.curselection()))
                self.range_entry[pnum].configure(foreground='black')
                self.range[pnum].set('Manual Range')
                self.range_entry[pnum].bind("<Button-1>", self.on_click)
                self.range_entry[pnum].bind('<Return>', lambda event: self.closerange(pnum))
                self.params[pnum]['range'] = self.range_entry[pnum].get().replace(' ', '')
                if self.params[pnum]['mode'] != 0:
                    self.params[pnum]['mode'] = 1
                self.params_queue.put_nowait([self.params[pnum], pnum])
            win.destroy()
        else:
            if self.range_entry[pnum].get() == 'Auto-Range' or self.range_entry[pnum].get() == 'Auto':
                self.range_entry[pnum].configure(foreground='grey')
                self.range[pnum].set('Auto Range')
                self.range_entry[pnum].bind("<Button-1>", self.on_click)
                self.range_entry[pnum].bind('<Return>', lambda event: self.closerange(pnum))
                self.params[pnum]['range'] = self.range_entry[pnum].get()
                if self.params[pnum]['mode'] != 0:
                    self.params[pnum]['mode'] = 1
                self.params_queue.put_nowait([self.params[pnum], pnum])
            else:
                self.range[pnum].set('Manual Range')
                self.range_entry[pnum].configure(foreground='black')
                self.range_entry[pnum].bind("<Button-1>", self.on_click)
                self.range_entry[pnum].bind('<Return>', lambda event: self.closerange(pnum))
                self.params[pnum]['range'] = self.range_entry[pnum].get().replace(' ', '')
                if self.params[pnum]['mode'] != 0:
                    self.params[pnum]['mode'] = 1
                self.params_queue.put_nowait([self.params[pnum], pnum])

    def cancel(self, win):
        win.destroy()

    def setunit(self, pnum, unit, rel=False):
        self.unit[pnum].set(unit)
        if unit == 'mW':
            self.ref_btn[pnum]['state'] = tk.DISABLED
        if unit == 'dB' or unit == 'dBm':
            unit = 'dBm'
            self.ref_btn[pnum]['state'] = tk.NORMAL
        self.params[pnum]['unit'] = unit
        if rel:
            self.params[pnum]['mode'] = 1
        else:
            self.params[pnum]['mode'] = 0
        self.params_queue.put_nowait([self.params[pnum], pnum])

    def setwav(self, pnum, wav):
        self.wav[pnum].set(wav)
        self.wav_entry[pnum].delete(0, END)
        self.wav_entry[pnum].insert(0, self.wav[pnum].get())
        self.wav_entry[pnum].configure(foreground='black')
        self.wav_entry[pnum].bind("<Button-1>", self.on_click)
        self.wav_entry[pnum].bind('<Return>', lambda event: self.setwav(pnum, self.wav_entry[pnum].get()))
        self.params[pnum]['wavelength'] = wav
        if self.params[pnum]['mode'] != 0:
            self.params[pnum]['mode'] = 1
        self.params_queue.put_nowait([self.params[pnum], pnum])

    def setatime(self, pnum, atime):
        atime.replace(' ', '')
        self.avgtime[pnum].set(atime)
        self.avg_entry[pnum].delete(0, END)
        self.avg_entry[pnum].insert(0, self.avgtime[pnum].get())
        self.avg_entry[pnum].configure(foreground='black')
        self.avg_entry[pnum].bind("<Button-1>", self.on_click)
        self.avg_entry[pnum].bind('<Return>', lambda event: self.setatime(pnum, self.avg_entry[pnum].get()))
        self.params[pnum]['average'] = atime
        if self.params[pnum]['mode'] != 0:
            self.params[pnum]['mode'] = 1
        self.params_queue.put_nowait([self.params[pnum], pnum])

    def dark(self, pnum):
        state = []
        power = []
        for p in range(4):
            state.append(self.state[p])
            power.append(self.powerread[p].get())
            self.wav850_btn[p]['state'] = tk.DISABLED
            self.wav1310_btn[p]['state'] = tk.DISABLED
            self.wav1490_btn[p]['state'] = tk.DISABLED
            self.wav1550_btn[p]['state'] = tk.DISABLED
            self.wav1625_btn[p]['state'] = tk.DISABLED
            self.avg_btn[p]['state'] = tk.DISABLED
            self.range_btn[p]['state'] = tk.DISABLED
            self.W_btn[p]['state'] = tk.DISABLED
            self.dbm_btn[p]['state'] = tk.DISABLED
            self.db_btn[p]['state'] = tk.DISABLED
            self.dark_btn[p]['state'] = tk.DISABLED
            self.ref_btn[p]['state'] = tk.DISABLED
            self.start_btn[p]['state'] = tk.DISABLED
            self.play_btn[p]['state'] = tk.DISABLED
            if self.state[p]:
                self.state[p] = not self.state[p]
        self.stat_queue.put(self.state)
        if self.live_thread is not None:
            while self.live_thread.is_alive():
                time.sleep(0.05)
        self.darkall_btn['state'] = tk.DISABLED
        if self.instrument is not None:
            device = self.instrument
        else:
            device = self.instrumentip
        if pnum != 'All':
            self.powerread[pnum].set('Darking...')
        else:
            for p in range(4):
                self.powerread[p].set('Darking...')
        # self.update()
        self.dark_thread = Dark(device, pnum)
        self.dark_thread.start()
        self.monitor(self.dark_thread, True, power, state)
        # key.dark(device, pnum)
        # self.darkall_btn['state'] = tk.NORMAL
        # for p in range(4):
        #     self.powerread[p].set(power[p])
        #     if state[p]:
        #         self.pauseplay(p)
        #         self.wav850_btn[p]['state'] = tk.DISABLED
        #         self.wav1310_btn[p]['state'] = tk.NORMAL
        #         self.wav1490_btn[p]['state'] = tk.NORMAL
        #         self.wav1550_btn[p]['state'] = tk.NORMAL
        #         self.wav1625_btn[p]['state'] = tk.NORMAL
        #         self.avg_btn[p]['state'] = tk.NORMAL
        #         self.range_btn[p]['state'] = tk.NORMAL
        #         self.W_btn[p]['state'] = tk.NORMAL
        #         self.dbm_btn[p]['state'] = tk.NORMAL
        #         self.db_btn[p]['state'] = tk.NORMAL
        #         self.dark_btn[p]['state'] = tk.NORMAL
        #         self.ref_btn[p]['state'] = tk.NORMAL
        #         self.play_btn[p]['state'] = tk.NORMAL
        #     else:
        #         self.start_btn[p]['state'] = tk.NORMAL

    def ref(self, pnum):
        self.unit[pnum].set('dB')
        self.params[pnum]['unit'] = 'dBm'
        self.params[pnum]['mode'] = 2
        self.params_queue.put_nowait([self.params[pnum], pnum])

    def monitor(self, thread, dark=False, power=None, state=None):
        if dark:
            if thread.is_alive():
                self.after(10, lambda: self.monitor(thread, True, power, state))
            else:
                self.darkall_btn['state'] = tk.NORMAL
                for p in range(4):
                    self.powerread[p].set(power[p])
                    if state[p]:
                        self.pauseplay(p)
                        self.wav850_btn[p]['state'] = tk.DISABLED
                        self.wav1310_btn[p]['state'] = tk.NORMAL
                        self.wav1490_btn[p]['state'] = tk.NORMAL
                        self.wav1550_btn[p]['state'] = tk.NORMAL
                        self.wav1625_btn[p]['state'] = tk.NORMAL
                        self.avg_btn[p]['state'] = tk.NORMAL
                        self.range_btn[p]['state'] = tk.NORMAL
                        self.W_btn[p]['state'] = tk.NORMAL
                        self.dbm_btn[p]['state'] = tk.NORMAL
                        self.db_btn[p]['state'] = tk.NORMAL
                        self.dark_btn[p]['state'] = tk.NORMAL
                        self.ref_btn[p]['state'] = tk.NORMAL
                        self.play_btn[p]['state'] = tk.NORMAL
                    else:
                        self.start_btn[p]['state'] = tk.NORMAL
        else:
            if thread.is_alive() and any(self.state):
                try:
                    e = self.except_queue.get_nowait()
                    if e[1]:
                        self.deviceip.set(str(e[0]))
                        self.deviceip_lbl.configure(foreground='red')
                        self.instrumentip = None
                    else:
                        self.device.set(str(e[0]))
                        self.device_lbl.configure(foreground='red')
                        self.instrument = None
                    for p in range(4):
                        self.state[p] = False
                        if self.instrument or self.instrumentip:
                            self.start_btn[p]['state'] = tk.NORMAL
                        else:
                            self.start_btn[p]['state'] = tk.DISABLED
                        self.wav850_btn[p]['state'] = tk.DISABLED
                        self.wav1310_btn[p]['state'] = tk.DISABLED
                        self.wav1490_btn[p]['state'] = tk.DISABLED
                        self.wav1550_btn[p]['state'] = tk.DISABLED
                        self.wav1625_btn[p]['state'] = tk.DISABLED
                        self.avg_btn[p]['state'] = tk.DISABLED
                        self.range_btn[p]['state'] = tk.DISABLED
                        self.W_btn[p]['state'] = tk.DISABLED
                        self.dbm_btn[p]['state'] = tk.DISABLED
                        self.db_btn[p]['state'] = tk.DISABLED
                        self.dark_btn[p]['state'] = tk.DISABLED
                        self.ref_btn[p]['state'] = tk.DISABLED
                        self.play_btn[p]['state'] = tk.DISABLED
                        self.stop_btn['state'] = tk.DISABLED
                        self.powerread[p].set('---.---')
                except queue.Empty:
                    pass
                try:
                    power = self.pow_queue.get_nowait()
                    for p in range(4):
                        if self.state[p]:
                            if self.params[p]['unit'] == 'mW':
                                if power[p] > 1e-1:
                                    self.unit[p].set('mW')
                                    self.powerread[p].set('> 100')
                                elif 1e-1 > power[p] >= 1e-3:
                                    self.unit[p].set('mW')
                                    self.powerread[p].set(format(1e3 * power[p], '.3f'))
                                elif 1e-3 > power[p] >= 1e-6:
                                    self.unit[p].set('\xb5W')
                                    self.powerread[p].set(format(1e6 * power[p], '.3f'))
                                elif 1e-6 > power[p] >= 1e-9:
                                    self.unit[p].set('nW')
                                    self.powerread[p].set(format(1e9 * power[p], '.3f'))
                                else:
                                    self.unit[p].set('pW')
                                    self.powerread[p].set(format(1e12 * power[p], '.3f'))
                            else:
                                if power[p] > 20 and self.unit[p].get() == 'dBm':
                                    self.powerread[p].set('> +20.0')
                                else:
                                    if power[p] >= 0:
                                        if power[p] >= 120:
                                            self.powerread[p].set('> +120.0')
                                        else:
                                            self.powerread[p].set('+' + format(power[p], '.4f'))
                                    else:
                                        self.powerread[p].set(format(power[p], '.4f'))
                    self.after(10, lambda: self.monitor(thread))
                except queue.Empty:
                    self.after(10, lambda: self.monitor(thread))
            else:
                try:
                    e = self.except_queue.get_nowait()
                    if e[1]:
                        self.deviceip.set(str(e[0]))
                        self.deviceip_lbl.configure(foreground='red')
                        self.instrumentip = None
                    else:
                        self.device.set(str(e[0]))
                        self.device_lbl.configure(foreground='red')
                        self.instrument = None
                    for p in range(4):
                        self.state[p] = False
                        if self.instrument or self.instrumentip:
                            self.start_btn[p]['state'] = tk.NORMAL
                        else:
                            self.start_btn[p]['state'] = tk.DISABLED
                        self.wav850_btn[p]['state'] = tk.DISABLED
                        self.wav1310_btn[p]['state'] = tk.DISABLED
                        self.wav1490_btn[p]['state'] = tk.DISABLED
                        self.wav1550_btn[p]['state'] = tk.DISABLED
                        self.wav1625_btn[p]['state'] = tk.DISABLED
                        self.avg_btn[p]['state'] = tk.DISABLED
                        self.range_btn[p]['state'] = tk.DISABLED
                        self.W_btn[p]['state'] = tk.DISABLED
                        self.dbm_btn[p]['state'] = tk.DISABLED
                        self.db_btn[p]['state'] = tk.DISABLED
                        self.dark_btn[p]['state'] = tk.DISABLED
                        self.ref_btn[p]['state'] = tk.DISABLED
                        self.play_btn[p]['state'] = tk.DISABLED
                        self.stop_btn['state'] = tk.DISABLED
                        self.powerread[p].set('---.---')
                except queue.Empty:
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
        self.db_btn[pnum]['state'] = tk.NORMAL
        self.dark_btn[pnum]['state'] = tk.NORMAL
        self.ref_btn[pnum]['state'] = tk.NORMAL
        self.start_btn[pnum]['state'] = tk.DISABLED
        self.play_btn[pnum]['state'] = tk.NORMAL
        self.stop_btn['state'] = tk.NORMAL
        self.state[pnum] = True
        self.setwav(pnum, self.params[pnum]['wavelength'])
        self.setunit(pnum, self.params[pnum]['unit'])
        self.setatime(pnum, self.params[pnum]['average'])
        self.closerange(pnum)
        while not self.params_queue.empty():
            try:
                self.params_queue.get(False)
            except queue.Empty:
                continue
            self.params_queue.task_done()
        if self.live_thread is not None and self.live_thread.is_alive():
            pass
        else:
            if self.instrument is not None:
                device = self.instrument
                ip = False
            else:
                device = self.instrumentip
                ip = True
            self.live_thread = Live(device, self.state, self.params, self.stat_queue, self.pow_queue, self.except_queue, self.params_queue, ip)
            self.live_thread.start()
            self.monitor(self.live_thread)

    def stop(self):
        for p in range(4):
            self.state[p] = False
            self.start_btn[p]['state'] = tk.NORMAL
            self.wav850_btn[p]['state'] = tk.DISABLED
            self.wav1310_btn[p]['state'] = tk.DISABLED
            self.wav1490_btn[p]['state'] = tk.DISABLED
            self.wav1550_btn[p]['state'] = tk.DISABLED
            self.wav1625_btn[p]['state'] = tk.DISABLED
            self.avg_btn[p]['state'] = tk.DISABLED
            self.range_btn[p]['state'] = tk.DISABLED
            self.W_btn[p]['state'] = tk.DISABLED
            self.dbm_btn[p]['state'] = tk.DISABLED
            self.db_btn[p]['state'] = tk.DISABLED
            self.dark_btn[p]['state'] = tk.DISABLED
            self.ref_btn[p]['state'] = tk.DISABLED
            self.play_btn[p]['state'] = tk.DISABLED
            self.stop_btn['state'] = tk.DISABLED
            self.powerread[p].set('---.---')
        self.stat_queue.put(self.state)

    def pauseplay(self, pnum):
        if not any(self.state):
            self.state[pnum] = not self.state[pnum]
            self.stat_queue.put(self.state)
            if self.instrument is not None:
                device = self.instrument
                ip = False
            else:
                device = self.instrumentip
                ip = True
            while not self.pow_queue.empty():
                try:
                    self.pow_queue.get(False)
                except queue.Empty:
                    continue
                self.pow_queue.task_done()
            self.stop_btn['state'] = tk.NORMAL
            self.live_thread = Live(device, self.state, self.params, self.stat_queue, self.pow_queue, self.except_queue, self.params_queue, ip, True)
            self.live_thread.start()
            self.monitor(self.live_thread)
        else:
            self.state[pnum] = not self.state[pnum]
            self.stat_queue.put(self.state)


class Live(Thread):
    def __init__(self, device, state, params, stat_queue, pow_queue, except_queue, params_queue, ip, pause=False):
        super().__init__()
        self.device = device
        self.state = state
        self.params = params
        self.stat_queue = stat_queue
        self.pow_queue = pow_queue
        self.except_queue = except_queue
        self.params_queue = params_queue
        self.ip = ip
        self.pause = pause
        self.status = [str(i) for i in self.state]

    def run(self):
        try:
            for p in range(4):
                key.conttrig(self.device, p, 1)
                key.setwav(self.device, p, self.params[p]['wavelength'])
                key.setatime(self.device, p, self.params[p]['average'])
                key.setrange(self.device, p, self.params[p]['range'])
                key.setunit(self.device, p, self.params[p]['unit'])
                key.setmode(self.device, p, self.params[p]['mode'])
                if not self.pause:
                    key.reference(self.device, p, True)
        except Exception as e:
            self.except_queue.put(['N7744A timed out', self.ip])
            self.status = ['False', 'False', 'False', 'False']
            pass
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
                key.setmode(self.device, para[1], para[0]['mode'])
                if para[0]['mode'] == 2:
                    key.reference(self.device, para[1])
            except queue.Empty:
                pass
            except Exception as e:
                self.except_queue.put(['N7744A timed out', self.ip])
                self.status = ['False', 'False', 'False', 'False']
            try:
                if not self.ip:
                    time.sleep(0.05)
                else:
                    time.sleep(0.1)
                readpow = key.readpow(self.device)
                self.pow_queue.put_nowait(readpow)
            except Exception as e:
                self.except_queue.put(['N7744A timed out', self.ip])
                self.status = ['False', 'False', 'False', 'False']


class Dark(Thread):
    def __init__(self, device, pnum):
        super().__init__()
        self.device = device
        self.pnum = pnum

    def run(self):
        key.dark(self.device, self.pnum)


if __name__ == "__main__":
    App().mainloop()
