#!/usr/bin/env python3

import re
import time
from queue import Queue
import subprocess
import platform
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk

try:
    from ctypes import windll
    windll.chcore.SetProcessDpiAwareness(1)
except:
    pass

numberOfRows = 5
ListOfIntinalIPs = ['1.1.1.1', 'www.google.com']
if len(ListOfIntinalIPs) > numberOfRows:
    numberOfRows = len(ListOfIntinalIPs)
autostart = True   # autostart list of IP address/URL's


class MainPingerGui():
    def __init__(self, mainGui):
        global numberOfRows, ListOfIntinalIPs, autostart
        self.numberOfRows = numberOfRows
        # global ListOfIntinalIPs
        self.ListOfIntinalIPs = ListOfIntinalIPs
        # global autostart
        self.autostart = autostart
        self.print_lock = threading.Lock()
        self.mainGui = mainGui
        self.mainGui.title('Multi Py Pinger - by Si')
        # self.mainGui.iconbitmap('LMarble.ico')
        self.print_lock = threading.Lock()
        if platform.system().lower() == 'windows':
            self.info = subprocess.STARTUPINFO()
            self.info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.info.wShowWindow = subprocess.SW_HIDE

        self.s = ttk.Style()
        self.s.theme_use('clam')
        self.makeframe()
        # self.mainGui.configure(background='blue')
        self.oldtimer = []
        self.timerControl = 1
        for t in range(self.numberOfRows):
            self.oldtimer.append('Never')
        self.importIPList()

    def makeframe(self):
        self.frameMain = tk.Frame(self.mainGui, bg='#8fe4f7')
        self.frameMain.grid(row=0, column=0)
        listOfHeaders = ['Go', 'Address/URL',
                         'Resolved to', 'Responce (ms)', 'Last seen', 'Last Time Offline']
        for hcol, header in enumerate(listOfHeaders):
            headerlbl = ttk.Label(self.frameMain, text=header)
            headerlbl.configure(anchor='center')
            headerlbl.grid(row=0, column=hcol, sticky='EW')

        self.chkBx = []
        self.entryBx = []
        self.entryVal = []
        self.chkVar = []
        self.lblidx = []
        self.lblVar = []

        for i in range(self.numberOfRows):
            tval = tk.StringVar()
            tval.set('0')
            eval = tk.StringVar()
            cBtn = ttk.Checkbutton(
                self.frameMain, variable=tval, command=lambda CbtnRow=i: self.CheckButtonFunction(CbtnRow))
            cBtn.state(['!alternate'])
            cBtn.grid(row=(i+1), column=0)
            self.chkBx.append(cBtn)
            self.chkVar.append(tval)
            eBox = tk.Entry(
                self.frameMain, textvariable=eval, background='yellow', foreground='Black', justify='center', width=24)
            eBox.grid(row=(i+1), column=1, ipadx=2, pady=2)
            self.entryBx.append(eBox)
            self.entryVal.append(eval)
            self.lblidx.append([])
            self.lblVar.append([])
            for n in range(4):
                lval = tk.StringVar()
                lbl = ttk.Label(self.frameMain, textvariable=lval)
                lbl.configure(anchor='center')
                lbl.grid(row=(i+1), column=(n+2),
                         sticky='EW', ipadx=2, pady=2)
                self.lblidx[i].append(lbl)
                self.lblVar[i].append(lval)

    def importIPList(self):
        for n,  ip in enumerate(self.ListOfIntinalIPs):
            self.entryVal[n].set(ip)
            if self.autostart:
                # print('autostart')
                self.chkVar[n].set('1')
                self.chkBx[n].state(['selected'])
                self.CheckButtonFunction(n)

    def CheckButtonFunction(self, index1):
        if int(self.chkVar[index1].get()):
            self.oldtimer[index1] = 'Never'
            self.entryBx[index1].configure(state='disabled')
            self.lblVar[index1][3].set('')
        else:
            self.entryBx[index1].configure(state='normal')
            self.setcolour2('white', index1)
        self.hosts = []
        goVar = 0
        shinter = 0
        for i in range(numberOfRows):
            if int(self.chkVar[i].get()):
                self.hosts.append([])
                self.hosts[shinter].append(self.entryBx[i].get())
                self.hosts[shinter].append(i)
                shinter += 1
            goVar = goVar + int(self.chkVar[i].get())
        if goVar and self.timerControl:
            self.pingerControl(index1)
        if not goVar:
            self.mainGui.after_cancel(self.timerFunc2)
            self.timerControl = 1
            # print('stopped')

    def pingerControl(self, index1):
        self.results = []
        self.timerControl = 0
        # print('Started')
        self.runPinger()
        self.timerFunc2 = self.mainGui.after(
            1000, lambda: self.pingerControl(index1))

    def setcolour2(self, colourToBeSet, indexlineA):
        self.entryBx[indexlineA].configure(
            background=colourToBeSet, disabledbackground=colourToBeSet, disabledforeground='black')
        for m in range(4):
            self.lblidx[indexlineA][m].config(background=colourToBeSet)

    def pingsweep(self, ip):
        # for windows:   -n is ping count, -w is wait (ms)
        # for linux: -c is ping count, -w is wait (ms)
        # I didn't test subprocess in linux, but know the ping count must change if OS changes
        if platform.system().lower() == 'windows':
            output = str(subprocess.Popen(['ping', '-n', '1', '-w', '250', self.hosts[ip][0]],
                                          stdout=subprocess.PIPE, startupinfo=self.info).communicate()[0])
        else:
            output = str(subprocess.Popen(["ping", self.hosts[ip][0], '-c', '1', '-t', '1'],
                                          stdout=subprocess.PIPE, shell=False).communicate()[0])

        with self.print_lock:

            if platform.system().lower() == 'windows':
                patternTime = re.compile(r'Average = (\d+\S\S)')
                patternip = re.compile(r'\[([a-zA-Z0-9,:\.]+)\]')
            else:
                patternTime = re.compile(r'time=(\d+\S\S)')
                patternip = re.compile(r'\(([a-zA-Z0-9,:\.]+)\)')

            matchTime = (patternTime.search(output)).group(
                1) if patternTime.search(output) else patternTime.search(output)
            matchip = (patternip.search(output)).group(
                1) if patternip.search(output) else patternip.search(output)

            # print(matchTime, ' ', matchip, ' ', self.now.strftime('%X'))
            self.now = datetime.now()
            self.results[ip].append(self.hosts[ip][1])
            self.results[ip].append(matchip)
            self.results[ip].append(matchTime)
            self.results[ip].append((self.now.strftime('%X')))

    def threader(self):
        while True:
            worker = self.q.get()
            self.results.append([])
            self.pingsweep(worker)
            self.q.task_done()

    def runPinger(self):

        startTime = time.time()
        self.q = Queue()

        for x in range(6):
            t = threading.Thread(target=self.threader)
            t.daemon = True
            t.start()

        for worker in range(len(self.hosts)):
            self.q.put(worker)

        self.q.join()
        self.resultsToScreen()
        runtime = float("%0.2f" % (time.time() - startTime))
        # print("Run Time: ", runtime, "seconds")

    def resultsToScreen(self):
        for i in range(len(self.results)):
            index1 = self.results[i][0]
            if self.results[i][2]:
                self.lblVar[index1][0].set(self.results[i][1])
                self.lblVar[index1][1].set(self.results[i][2])
                self.lblVar[index1][2].set(self.results[i][3])
                self.oldtimer[index1] = self.now
                self.setcolour2('#59ff80', index1)
            else:
                self.lblVar[index1][0].set('')
                self.lblVar[index1][1].set('Failed')
                if self.oldtimer[index1] == 'Never':
                    self.lblVar[index1][2].set('Never')
                else:
                    self.lblVar[index1][2].set(
                        self.oldtimer[index1].strftime('%X'))
                    self.lblVar[index1][3].set(
                        str(self.now-self.oldtimer[index1])[: 7])
                self.setcolour2('#ff5145', index1)


def main():
    root = tk.Tk()
    app = MainPingerGui(root)
    root.mainloop()


if __name__ == '__main__':
    main()
