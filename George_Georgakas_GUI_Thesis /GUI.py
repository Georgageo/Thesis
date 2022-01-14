import cmd
import signal
import subprocess
import tkinter as tk
import tkinter.ttk
from tkinter import *
from tkinter import messagebox
import threading


import time

import os

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch, Controller
from multiprocessing import Process
from synchrophasor.pmu import Pmu

from mininet.topolib import TreeNet
from mininet.topo import LinearTopo, MinimalTopoNew, SingleSwitchTopo



class NewWindow():

    def __init__(self, root, net, PMU_list, PDC_list, Statistics, streamButton):
        self.root = root
        self.StreamButton = streamButton
        self.net = net
        self.FramePmuList = PMU_list
        self.FramePdcList = PDC_list
        self.Stats = Statistics
        self.hosts = {}
        self.pmu = None
        self.Flag = False
        self.FLag1 = False #flag gia thn epanemfanisi tou PdcList

        self.createNewWindow()
        self.label()
        self.widget()

    def createNewWindow(self):
        self.window = tk.Toplevel(self.root)
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.window.geometry('400x400+700+350')
        self.window.title('HostsStreaming')
        self.x, self.y = self.window.winfo_x(), self.window.winfo_y()

    def label(self):
        self.label2 = tk.LabelFrame(self.window, text = 'Hosts')  #Label me ta PMU
        self.label2.pack(fill = 'both', padx = 2, pady = 2)
        self.label3 = tk.Label(self.window) #Label gia ta buttons
        self.label3.pack(side = 'bottom')

    def widget(self):
        i = 0
        for h in self.net.hosts:
            self.hosts[str(h)] = h.IP()
        # self.Entry1 = tk.Entry(self.label2, text = 'Enter the Name')
        # self.Entry1.pack()
        self.Button = tk.Button(self.label3, text = 'cancel', command = self.cancel) #Button cancel gia katastrofh tou parathurou me tous PMU
        self.Button.pack(side = RIGHT)
        self.Button1 = tk.Button(self.label3, text='stream to', state = 'disabled', command = self.PdcListMenu) #Button stream to gia anoigma parathurou me tous PDC
        self.Button1.pack()
        self.Button1.bind("<Enter>", self.enable)

        self.HostList = tk.Listbox(self.label2, font='Calibri 25', height=7, width=20) #ListBox pou periexei ta PMU
        self.HostList.pack()
        for key, value in self.hosts.items():
            if 'PMU' in key:
                self.HostList.insert(i, f'{key} : {value}')
                i += 1

    def PdcListMenu(self):
        self.FLag1 = True
        self.Flag = True
        self.Button1.config(state = 'disabled')
        for i in self.HostList.curselection():
            self.host, self.ip = self.HostList.get(i).split(':')
        self.host = self.host.strip()
        self.ip = self.ip.strip()

        for child in self.label2.winfo_children():
            child.configure(state='disable')
        for child in self.label3.winfo_children():
            child.configure(state='disable')

        i = 0
        x,y = self.window.winfo_x(), self.window.winfo_y()

        self.PDCsList = tk.Toplevel(self.window)
        self.PDCsList.protocol("WM_DELETE_WINDOW", self.close_PdcListWindow)
        self.PDCsList.title("StreamTo..")
        self.PDCsList.geometry('+{}+{}'.format(x+400,y+400))
        self.LabelPdcList = tk.Label(self.PDCsList)
        self.LabelPdcList.pack()
        self.LabelButtonsPdc = tk.Label(self.PDCsList)
        self.LabelButtonsPdc.pack()
        self.StartStreamButton = tk.Button(self.LabelButtonsPdc, text = "start", command = self.startStream , state = 'disable')
        self.StartStreamButton.pack(side = 'left')
        self.ShowStreamButton = tk.Button(self.LabelButtonsPdc ,text = 'show', command = self.showData, state = 'disable')
        self.ShowStreamButton.pack(side = 'left')
        self.CancelPdcButtom = tk.Button(self.LabelButtonsPdc, text="cancel", command=self.exit)
        self.CancelPdcButtom.pack(side='left')
        self.PdcList = tk.Listbox(self.LabelPdcList, font='Calibri 25', height=5, width=20)
        self.PdcList.pack()
        self.StartStreamButton.bind("<Enter>",self.enableStartStreamButton)
        for key, value in self.hosts.items():
            if 'PDC' in key:
                self.PdcList.insert(i, f'{key} : {value}')
                i += 1

    def startStream(self):
        self.ShowStreamButton.config(state = 'normal')
        self.StartStreamButton.config(state = 'disable')
        self.p3 = Process(target=self.PdcListMenu)
        self.p3.start()
        self.p3.join()
        time.sleep(2)
        self.p1 = Process(target=self.open_pmu)
        self.p1.start()
        self.p2 = Process(target=self.open_pdc)
        self.p2.start()

        self.p1.join()
        self.p2.join()


    def open_pmu(self):
        self.pmu.cmdPrint(f'sudo python3 ./tinyPMU.py --pmu {self.ip} > PMU_Conn.txt')
         # self.pmu.cmdPrint(f'sudo python3 ./../PyPMU/examples/tinyPMU.py --pmu {self.ip} > PMU_Conn.txt')

    def open_pdc(self):

        time.sleep(1)
        self.pdc.cmdPrint(f'sudo python3 ./tinyPDC.py --pdc {self.ip} > PDC_Conn.txt')
        # self.pdc.cmdPrint(f'sudo python3 ./../PyPMU/examples/tinyPDC.py --pdc {self.ip} > PDC_Conn.txt')

    def close_window(self):
        self.StreamButton['state'] = 'normal'
        self.window.destroy()

    def close_PdcListWindow(self):
        self.Button1['state'] = 'normal'
        self.PDCsList.destroy()
        for child in self.label2.winfo_children():
            child.configure(state='normal')
        for child in self.label3.winfo_children():
            child.configure(state='normal')
    # def pmu_thread(self, pmu, ip):
    #     # print("Hello Thread2")
    #     # print("Hello Thread2 after sleep")
    #     # x2 = threading.Thread(target=pdc_thread(pdc))
    #     # x2.start()
    #
    #     # pmu.cmd('cd')
    #
    #     pmu.cmdPrint(f'python3 ./../PyPMU/examples/tinyPMU.py --pmu {self.ip}')
    # def pdc_thread(self, pdc, ip):
    #     time.sleep(2)
    #     # print("Hello Thread1")
    #     pdc.cmd('cd')
    #     # pdc.cmd(f'xterm {pdc}')
    #     pdc.cmdPrint(f'python3 ./../PyPMU/examples/tinyPDC.py --pdc {self.ip}')




    def enableStartStreamButton(self,event):
        host = ''
        for i in self.PdcList.curselection():
            self.pdc, self.pdc_ip = self.PdcList.get(i).split(':')
        self.pdc_ip = self.pdc_ip.strip()
        self.pdc = self.pdc.strip()
        self.pmu = self.net.get(self.host)
        self.pdc = self.net.get(self.pdc)
        for i in self.PdcList.curselection():
            host = self.PdcList.get(i)
        if len(host) == 0:

            self.StartStreamButton.config(state = 'disabled')

        else:
            ping = self.pmu.cmdPrint(f'ping {self.pdc_ip} -c1')
            received = ping.split(',')[1]
            if int(received.strip()[0]) > 0:

                self.StartStreamButton.config(state='normal')



    def enable(self,event): #sunarthsh gia thn energopoihsh tou button stream to otan dialexoume enan h parapananw PMU
        host = ''
        if self.Flag == False:
            for i in self.HostList.curselection():
                host = self.HostList.get(i)

            if len(host) == 0:
                self.Button1.config(state = 'disabled')
            else:
                self.Button1.config(state='normal')
        else:
            self.Button1.config(state='disabled')

    def cancel(self):
        for child in self.root.winfo_children():
            if 'labelframe3' in str(child):
                for c in child.winfo_children():
                    if 'button2' in str(c):
                        c.config(state='normal')

        self.window.destroy()


    def exit(self):
        self.PDCsList.destroy()
        self.Flag = False
        self.FLag1 = False
        for child in self.label2.winfo_children():
            child.configure(state='normal')
        for child in self.label3.winfo_children():
            child.configure(state='normal')

    def showData(self):
        SentTime = []
        ReceivedTime = []
        self.ShowStreamButton['state'] = 'disabled'

        try:
            with open('PMU_Conn.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    l = line[:-1]
                    self.FramePmuList.insert(END,l)

                    if 'Send Time' in l:
                        SentTime.append(l[21:])
                        # print(l[21:])
                    if 'Total sent packets' in l:
                        Packets = l
                        a, TotalPmuPackets = Packets.strip().split(':')
        except:
            print("Could not find the PMU_Conn.txt")

        try:
            with open('PDC_Conn.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    l = line[:-1]
                    self.FramePdcList.insert(END, l)
                    if 'Delivered Time' in l:
                        ReceivedTime.append(l[25:])
                        # print(l[25:])
                    if 'Total Packets' in l:
                        Packets = l
                        a,TotalPdcPackets = Packets.strip().split(':')
        except:
            print("Could not find the PDC_Conn.txt")

        SentTime.pop()
        DelayTime = []
        TotalDelay = 0.0
        PacketLoss = int(TotalPmuPackets) - int(TotalPdcPackets)
        for i in range(len(SentTime)):
            hour1, min1, sec1 = SentTime[i].strip().split(':')
            hour2, min2, sec2 = ReceivedTime[i].strip().split(':')
            # print(f'Hour1:{hour1}   Min1:{min1}     sec1:{sec1}')
            # print(f'Hour2:{hour2}   Min2:{min2}     sec2:{sec2}')
            hour = int(hour2) - int(hour1)
            min = int(min2) - int(min1)
            sec = float(sec2) - float(sec1)
            delayTime = f'{hour}:{min}:{sec}'
            DelayTime.append(delayTime)
        with open('Statistics.txt', 'a', encoding='utf-8') as f:
            f.write(f'{self.host}:{self.ip}--->{self.pdc}:{self.pdc_ip}\n')
            for i in range(len(DelayTime)):
                h, m, s = DelayTime[i].split(':')

                if int(h) == 0 and int(m) == 0:
                    f.write(f'DelayTime of packet {i+1}: {float(s):.6f}sec\n')
                    TotalDelay+=float(s)
                else:
                    f.write(f'DelatTime:{DelayTime[i]}\n')
            f.write(f'Average Delay:{TotalDelay/float(TotalPmuPackets):.6f}sec\n')
            f.write(f'Total packet loss:{PacketLoss}\n\n')
        self.Stats.delete(0,END)
        with open('Statistics.txt', 'r', encoding='utf-8') as f:
            for l in f:
                self.Stats.insert(END,l[:-1])






class App():

    def __init__(self,root):
        # self.mn = Mininet
        # os.system('sudo fuser -k 6633/tcp')

        file = open('Statistics.txt', 'w')
        file.truncate()
        file.close()
        root.geometry('2000x2000+200+200')

        self.y = root.winfo_screenheight()
        self.x = root.winfo_screenwidth()
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        self.net = None
        self.flag = True
        self.hosts = {}
        self.font = 'Calibri 18'



        self.numbersplitPMU = StringVar()
        self.numbersplitPMU.set('')
        self.numbersplitPDC = StringVar()
        self.numbersplitPDC.set('')
        # self.ipText = tk.StringVar()  # για να ανανεωνονται οι ip στο frame2
        # self.ipText.set('10.0.0.0')

        self.root.title('PMU GUI')
        self.labelFrames()
        self.widgets()
        self.RunTopoFlag = False
        #self.widgets()

    def close_window(self):
        self.root.destroy()
        os.system('sudo mn -c')

    # ta parathura
    def labelFrames(self):

        # Grid.rowconfigure(self.root, 0, weight=1)
        # Grid.columnconfigure(self.root, 0, weight=1)
        # Grid.rowconfigure(self.root, 1, weight=2)
        # Grid.rowconfigure(self.root, 2, weight=2)
        # Grid.rowconfigure(self.root, 3, weight=2)
        # Grid.rowconfigure(self.root, 4, weight=2)

        # Grid.columnconfigure(self.root, 1, weight=2)


        self.label1 = tk.LabelFrame(self.root, text='TreeTopo') #Label me ta Entries
        self.label1.place(x=10, y=180)
        # self.label1.grid(row=1, column=0)

        self.label2 = tk.LabelFrame(self.root, text='HostsIP') #Label gia ta IP
        self.label2.place(x=10, y=420)
        # self.label2.grid(row=2, column=0)

        self.label3 = tk.LabelFrame(self.root)  #Label me ta koumpia run ,stop
        self.label3.place(x=10, y=980)
        # self.label3.grid(row=4, column=0)

        # self.label4 = tk.LabelFrame(self.root, text='Test')
        # self.label4.place(x=10, y=840)

        self.label5 = LabelFrame(self.root, text = "Topologies") #Label me ta RadioButtons
        self.label5.place(x=10, y=10)
        # self.label5.grid(row=0, column=0)

        self.label6 = LabelFrame(self.root , text = "Streaming") #Label gia thn kinhsh twn paketwn
        # self.label6.place(x=450, y=100)

        self.label7 = LabelFrame(self.root, text = 'Connectivity')
        self.label7.place(x=10, y=700)
        # self.label7.grid(row=3, column=0)

        self.FramePMU = LabelFrame(self.root, text = 'PMU Streaming')
        self.FramePMU.place(x = 500 , y = 10)
        # self.FramePMU.grid(row=0, column=1)

        self.FramePDC = LabelFrame(self.root, text = 'PDC Streaming')
        self.FramePDC.place(x = 500 , y = 520)
        # self.FramePDC.grid(row=1, column=1)
        self.StatsFrame = LabelFrame(self.root, text = 'Statistics')
        self.StatsFrame.place(x = 1200, y = 10)
        #

        # self.label2.pack(side='bottom', padx=5, pady=5)

    #ta antikeimena mesa sta parathura
    def widgets(self):


        #ta by default Entries και label του FrameLabel1

        self.info = tk.Label(self.label1, text='Insert Depth and Fanout of a TreeTopo', font=self.font)
        self.info.grid(row=0, column=0, columnspan=2)

        self.lb1 = tk.Label(self.label1, text="Depth", font='Calibri 12')
        self.lb1.grid(row=1, column=0)
        self.lb2 = tk.Label(self.label1, text="Fanout", font='Calibri 12')
        self.lb2.grid(row=2, column=0)
        self.lb3 = tk.Label(self.label1, text="PMUs", font='Calibri 12')
        self.lb3.grid(row=3, column=0)
        self.lb4 = tk.Label(self.label1, text="PDCs", font='Calibri 12')
        self.lb4.grid(row=4, column=0)

        self.Depth = tk.Entry(self.label1, font='Calibri 20', width=5)
        self.Depth.grid(row=1, column=1)
        self.Fanout = tk.Entry(self.label1, font='Calibri 20', width=5)
        self.Fanout.grid(row=2, column=1)
        self.PMUs = tk.Entry(self.label1, font='Calibri 20',textvariable=self.numbersplitPMU , width=5, state=DISABLED) # PMUs Entry
        self.PMUs.grid(row=3, column=1)
        self.PDCs = tk.Entry(self.label1, font='Calibri 20',textvariable=self.numbersplitPDC ,width=5, state=DISABLED) #PDCs Entry
        self.PDCs.grid(row=4, column=1)
        self.win = Label(self.label1)
        self.win.grid()
        self.next = Button(self.win, text='next', command = self.next1,state = 'disabled')
        self.next.pack(side=LEFT)
        self.pre = Button(self.win, text='back', command = self.back, state = 'disabled')
        self.pre.pack(side=LEFT)


        self.IpTable = tk.Label(self.label2, height = 15, width = 58)
        self.IpTable.pack()

        self.ConTable = tk.Label(self.label7, height = 15, width = 58)
        self.ConTable.pack()

        # self.StreamPmuTable = tk.Label(self.FramePMU, height = 26, width = 140)
        # self.StreamPmuTable.pack()

        # self.StreamPdcTable = tk.Label(self.FramePDC, height = 26, width = 140)
        # self.StreamPdcTable.pack()

        self.button = tk.Button(self.label3, text='run topo', command=self.startTopo , font = 'Calibri 10', state = 'disabled') #run Button
        self.button.pack(side = 'left')

        self.buttonPMU = tk.Button(self.label3, text='StartStream', command=self.open_Streaming, font='Calibri 10', state = 'disabled')
        self.buttonPMU.pack(side = 'left')

        self.button2 = tk.Button(self.label3, text='stop topo', command=self.exit, font='Calibri 10') #Stop Button
        self.button2['state'] = 'disabled'
        self.button2.pack(side='left')

        self.answer = tk.StringVar(self.label5,'TreeTopo')
        self.TreeButton = tk.Radiobutton(self.label5, text = "Tree Topo    ",font="Calibri 12", value = 'TreeTopo',
                                         variable = self.answer, command = self.choice, state = 'disabled')
        self.TreeButton.pack()
        self.LinearButton = tk.Radiobutton(self.label5, text="Linear Topo  ", font="Calibri 12", value = 'LinearTopo',
                                           variable = self.answer, command = self.choice)
        self.LinearButton.pack()
        self.SingleButton = tk.Radiobutton(self.label5, text="Single Topo  ", font="Calibri 12", value = 'SingleTopo',
                                           variable = self.answer , command = self.choice)
        self.SingleButton.pack()
        self.MinimalButton = tk.Radiobutton(self.label5, text="Minimal Topo", font="Calibri 12", value='MinimalTopo',
                                           variable=self.answer, command=self.choice)
        self.MinimalButton.pack()


        # self.submit = tk.Button(self.label5, text='submit', command=lambda: enable(self.label1.winfo_children()))
        # self.submit.pack()

        self.button.bind("<Enter>", self.enable)
        self.next.bind("<Enter>",self.NextButtonEnable)




        self.PmuStreamList = Listbox(self.FramePMU, font='Calibri 12', height = 23, width = 67)
        self.PmuStreamList.grid(row=0, column=0)

        #ScollBarY
        self.PmuStreamBarY = tk.Scrollbar(self.FramePMU)
        self.PmuStreamBarY.grid(row=0, column=1, sticky=N+S+E+W)
        self.PmuStreamList.config(yscrollcommand=self.PmuStreamBarY.set)
        self.PmuStreamBarY.config(command=self.PmuStreamList.yview)

        #ScrollBarX
        self.PmuStreamBarX = tk.Scrollbar(self.FramePMU, orient=HORIZONTAL)
        self.PmuStreamBarX.grid(row=1, column=0, sticky=N+S+E+W)
        self.PmuStreamList.config(xscrollcommand=self.PmuStreamBarX.set)
        self.PmuStreamBarX.config(command=self.PmuStreamList.xview)

        #
        self.PdcStreamList = Listbox(self.FramePDC, font='Calibri 12', height = 23, width = 67)
        self.PdcStreamList.grid(row=0, column=0)

        # ScollBarY
        self.PdcStreamBarY = tk.Scrollbar(self.FramePDC)
        self.PdcStreamBarY.grid(row=0, column=1, sticky=N+S+E+W)
        self.PdcStreamList.config(yscrollcommand=self.PdcStreamBarY.set)
        self.PdcStreamBarY.config(command=self.PdcStreamList.yview)

        # ScrollBarX
        self.PdcStreamBarX = tk.Scrollbar(self.FramePDC, orient=HORIZONTAL)
        self.PdcStreamBarX.grid(row=1, column=0, sticky=N + S + E + W)
        self.PdcStreamList.config(xscrollcommand=self.PdcStreamBarX.set)
        self.PdcStreamBarX.config(command=self.PdcStreamList.xview)

        self.Stats = Listbox(self.StatsFrame, font='Calibri 12', height=48 , width=65)
        self.Stats.grid(row=0, column=0)

        # ScollBarY
        self.StatsmBarY = tk.Scrollbar(self.StatsFrame)
        self.StatsmBarY.grid(row=0, column=1, sticky=N + S + E + W)
        self.Stats.config(yscrollcommand=self.StatsmBarY.set)
        self.StatsmBarY.config(command=self.Stats.yview)

        # ScrollBarX
        self.StatsmBarX = tk.Scrollbar(self.StatsFrame, orient=HORIZONTAL)
        self.StatsmBarX.grid(row=1, column=0, sticky=N + S + E + W)
        self.Stats.config(xscrollcommand=self.StatsmBarX.set)
        self.StatsmBarX.config(command=self.Stats.xview)

    def NextButtonEnable(self,event):
        if self.answer.get() == 'TreeTopo':
            try:
                if isinstance(int(self.Depth.get()), int) and isinstance(int(self.Fanout.get()), int):
                    self.next['state'] = 'normal'
                else:
                    self.next['state'] = 'disabled'
            except:
                self.next['state'] = 'disabled'

        else:
            try:
                if isinstance(int(self.Switches.get()), int) and isinstance(int(self.HostPerSwitch.get()), int):
                    self.next['state'] = 'normal'
                else:
                    self.next['state'] = 'disabled'
            except:
                self.next['state'] = 'disabled'



    def enable(self,event): #synarthsh gia energopoihsh tou run topo

        if self.RunTopoFlag == False:
            if self.answer.get() == "TreeTopo":

                try:
                    hosts = pow(int(self.Fanout.get()), int(self.Depth.get()))
                    PMU = int(self.PMUs.get())
                    PDC = int(self.PDCs.get())
                    if isinstance(int(self.PMUs.get()), int) and isinstance(int(self.PDCs.get()), int):
                        if hosts == PMU + PDC and hosts>1:
                            self.button['state'] = 'normal'
                        else:
                            self.button['state'] = 'disabled'
                except:
                    self.button['state'] = 'disabled'

            elif self.answer.get() == 'SingleTopo':
                try:
                    if isinstance(int(self.PMUs.get()),int) and isinstance(int(self.PDCs.get()),int)\
                            and int(self.PMUs.get()) >= 1 and int(self.PDCs.get()) >= 1:
                        self.button['state'] = 'normal'
                    else:
                        self.button['state'] = 'disabled'
                except:
                    self.button['state'] = 'disabled'

            elif self.answer.get() == 'LinearTopo':
                # print("TEST2")
                try:
                    hosts = int(self.PDCs.get()) + int(self.PMUs.get())

                    if isinstance(int(self.PMUs.get()), int) and isinstance(int(self.PDCs.get()), int):
                        if hosts == int(self.Switches.get()) * int(self.HostPerSwitch.get()) and hosts>1:
                            self.button['state'] = 'normal'
                        else:
                            self.button['state'] = 'disabled'
                except:
                    self.button['state'] = 'disabled'

            else:
                self.button['state'] = 'normal'
        else:
            self.button['state'] = 'disabled'

    def next1(self):

        # print(f'HalfHosts:{ totalHosts / 2}')
        # self.button['state'] = 'normal'
        if self.answer.get() == 'TreeTopo':
            if int(self.Depth.get()) == 1:
                totalHosts = int(self.Fanout.get())
            else:
                totalHosts = pow(int(self.Fanout.get()), int(self.Depth.get()))
            if totalHosts % 2 == 0:
                self.numbersplitPMU.set(f'{int(totalHosts / 2)}')
                self.numbersplitPDC.set(f'{int(totalHosts / 2)}')
            else:
                self.numbersplitPMU.set(f'{int(totalHosts / 2) + 1}')
                self.numbersplitPDC.set(f'{int(totalHosts / 2) }')
            self.next['state'] = 'disabled'
            self.pre['state'] = 'normal'
            self.Depth.config(state = 'disabled')
            self.Fanout.config(state='disabled')
            self.PMUs.config(state = 'normal')
            self.PDCs.config(state ='normal')
        else:
            totalHosts = int(self.Switches.get()) * int(self.HostPerSwitch.get())
            if totalHosts % 2 == 0:
                self.numbersplitPMU.set(f'{int(totalHosts / 2)}')
                self.numbersplitPDC.set(f'{int(totalHosts / 2)}')
            else:
                self.numbersplitPMU.set(f'{int(totalHosts / 2) + 1}')
                self.numbersplitPDC.set(f'{int(totalHosts / 2)}')
            self.next['state'] = 'disabled'
            self.pre['state'] = 'normal'
            self.Switches.config(state = 'disabled')
            self.HostPerSwitch.config(state = 'disabled')
            self.PMUs.config(state='normal')
            self.PDCs.config(state='normal')


    def back(self):
        if self.answer.get() == 'TreeTopo':
            self.button['state'] = 'disabled'
            self.numbersplitPMU.set('0')
            self.numbersplitPDC.set('0')
            self.pre['state'] = 'disabled'
            self.next['state'] = 'normal'
            self.Depth.config(state='normal')
            self.Fanout.config(state='normal')
            self.PMUs.config(state='disabled')
            self.PDCs.config(state='disabled')
        else:
            self.button['state'] = 'disabled'
            self.numbersplitPMU.set('0')
            self.numbersplitPDC.set('0')
            self.pre['state'] = 'disabled'
            self.next['state'] = 'normal'
            self.PMUs.config(state='disabled')
            self.PDCs.config(state='disabled')
            self.Switches.config(state='normal')
            self.HostPerSwitch.config(state='normal')

    def choice(self):
        self.label1.destroy()
        self.button['state'] = 'disabled'
        # print(f"Answer:{self.answer.get()}")
        if self.answer.get() == 'TreeTopo':

            self.label1 = tk.LabelFrame(self.root, text='TreeTopo')
            self.label1.place(x=10, y=180)
            self.TreeButton['state'] = 'disabled'
            self.LinearButton['state'] = 'normal'
            self.SingleButton['state'] = 'normal'
            self.MinimalButton['state'] = 'normal'
            self.numbersplitPMU.set('')
            self.numbersplitPDC.set('')
            self.info = tk.Label(self.label1, text='Insert Depth and Fanout of a TreeTopo', font=self.font)
            self.info.grid(row=0, column=0, columnspan=2)

            self.lb1 = tk.Label(self.label1, text="Depth", font='Calibri 12')
            self.lb1.grid(row=1, column=0)
            self.lb2 = tk.Label(self.label1, text="Fanout", font='Calibri 12')
            self.lb2.grid(row=2, column=0)
            self.lb3 = tk.Label(self.label1, text="PMUs", font='Calibri 12')
            self.lb3.grid(row=3, column=0)
            self.lb4 = tk.Label(self.label1, text="PDCs", font='Calibri 12')
            self.lb4.grid(row=4, column=0)

            self.Depth = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.Depth.grid(row=1, column=1)
            self.Fanout = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.Fanout.grid(row=2, column=1)
            self.PMUs = tk.Entry(self.label1, font='Calibri 20', textvariable=self.numbersplitPMU, width=5,
                                state=DISABLED)  # PMUs Entry
            self.PMUs.grid(row=3, column=1)
            self.PDCs = tk.Entry(self.label1, font='Calibri 20', textvariable=self.numbersplitPDC, width=5,
                                state=DISABLED)  # PDCs Entry
            self.PDCs.grid(row=4, column=1)
            self.win = Label(self.label1)
            self.win.grid()
            self.next = Button(self.win, text='next', command=self.next1, state = 'disable')
            self.next.pack(side=LEFT)
            self.pre = Button(self.win, text='back', command=self.back)
            self.pre.pack(side=LEFT)
            self.pre['state'] = 'disabled'
            self.next.bind("<Enter>", self.NextButtonEnable)

            # self.submit = Button(self.label1, text = 'Submit')
            # self.submit.grid(row=3, column=1)

        elif self.answer.get() == 'MinimalTopo':
            self.button['state'] = 'normal'
            self.label1 = tk.LabelFrame(self.root, text='MinimalTopo')
            self.label1.place(x=10, y=180)
            self.info = tk.Label(self.label1, text='Two Hosts and one Switch', font='Calibri 26')
            self.info.grid(row=0, column=0, columnspan=2)
            self.TreeButton['state'] = 'normal'
            self.LinearButton['state'] = 'normal'
            self.SingleButton['state'] = 'normal'
            self.MinimalButton['state'] = 'disabled'
            self.lb1 = tk.Label(self.label1, text="PMUs", font='Calibri 12')
            self.lb1.grid(row=1, column=0)
            self.lb2 = tk.Label(self.label1, text="PDCs", font='Calibri 12')
            self.lb2.grid(row=2, column=0)

            self.PMUs = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.PMUs.grid(row=1, column=1)
            self.PMUs.insert(END,1)
            self.PMUs.config(state=DISABLED)
            self.PDCs = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.PDCs.grid(row=2, column=1)
            self.PDCs.insert(END,1)
            self.PDCs.config(state=DISABLED)

        elif self.answer.get() == 'SingleTopo':
            self.label1 = tk.LabelFrame(self.root, text='SingleTopo')
            self.label1.place(x=10, y=180)
            self.info = tk.Label(self.label1, text='Insert Number of PMUs and PDCs', font='Calibri 21')
            self.info.grid(row=0, column=0, columnspan=2)
            self.TreeButton['state'] = 'normal'
            self.LinearButton['state'] = 'normal'
            self.SingleButton['state'] = 'disabled'
            self.MinimalButton['state'] = 'normal'
            self.lb1 = tk.Label(self.label1, text="PMUs", font='Calibri 12')
            self.lb1.grid(row=1, column=0)
            self.lb2 = tk.Label(self.label1, text="PDCs", font='Calibri 12')
            self.lb2.grid(row=2, column=0)

            self.PMUs = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.PMUs.grid(row=1, column=1)
            self.PDCs = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.PDCs.grid(row=2, column=1)

        else:
            self.label1 = tk.LabelFrame(self.root, text='LinearTopo')
            self.label1.place(x=10, y=180)
            self.info = tk.Label(self.label1, text='Insert Number of Hosts and Switches', font='Calibri 19')
            self.info.grid(row=0, column=0, columnspan=2)
            self.TreeButton['state'] = 'normal'
            self.LinearButton['state'] = 'disabled'
            self.SingleButton['state'] = 'normal'
            self.MinimalButton['state'] = 'normal'
            self.lb1 = tk.Label(self.label1, text="PMUs", font='Calibri 12')
            self.lb1.grid(row=3, column=0)
            self.lb2 = tk.Label(self.label1, text="PDCs", font='Calibri 12')
            self.lb2.grid(row=4, column=0)
            self.lb3 = tk.Label(self.label1, text="Switches", font='Calibri 12')
            self.lb3.grid(row=1, column=0)
            self.lb4 = tk.Label(self.label1, text="Host/s", font='Calibri 12')
            self.lb4.grid(row=2, column=0)

            self.Switches = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.Switches.grid(row=1, column=1)
            self.HostPerSwitch = tk.Entry(self.label1, font='Calibri 20', width=5)
            self.HostPerSwitch.grid(row=2, column=1)
            self.PMUs = tk.Entry(self.label1, font='Calibri 20', textvariable=self.numbersplitPMU,width=5, state = 'disabled')
            self.PMUs.grid(row=3, column=1)
            self.PDCs = tk.Entry(self.label1, font='Calibri 20', textvariable=self.numbersplitPDC,width=5, state = 'disabled')
            self.PDCs.grid(row=4, column=1)

            self.win = Label(self.label1)
            self.win.grid()
            self.next = Button(self.win, text='next', command=self.next1, state = 'disable')
            self.next.pack(side=LEFT)
            self.pre = Button(self.win, text='back', command=self.back)
            self.pre.pack(side=LEFT)
            self.pre['state'] = 'disabled'
            self.next.bind("<Enter>", self.NextButtonEnable)


    def updateIpFrame(self):

        # self.text1 = self.PMUs.get()
        # self.text2 = self.PDCs.get()
        # self.text3 = self.Switches.get()
        self.TreeButton.config(state=DISABLED)
        self.SingleButton.config(state=DISABLED)
        self.LinearButton.config(state=DISABLED)
        self.MinimalButton.config(state=DISABLED)
        self.buttonPMU.config(state='normal')



        for child in self.label1.winfo_children():
            child.configure(state='disable')
        if not self.hosts:
            self.IpTable.destroy()
            i=0
            for h in self.net.hosts:
                self.hosts[str(h)] = h.IP()

            self.button2['state'] = 'active'
            self.HostList = tk.Listbox(self.label2, font='Calibri 25', height=6, width=22)
            self.HostList.pack(side=LEFT)
            self.sbar = tk.Scrollbar(self.label2)
            self.sbar.pack(side=RIGHT, fill=Y)
            self.HostList.config(yscrollcommand=self.sbar.set)
            self.sbar.config(command=self.HostList.yview)
            for key, value in self.hosts.items():
                self.HostList.insert(i,f'{key} : {value}')
                i+=1

            self.button['state'] = 'disabled'
            self.buttonPMU['state'] = 'active'

            if self.answer.get() == 'TreeTopo':
                self.next['state'] = DISABLED
                self.pre['state'] = DISABLED
                self.ConTable.destroy()
                self.ConList = tk.Listbox(self.label7, font = 'Calibri 25', height=6, width=22)
                self.ConList.grid(row=0, column=0)
                self.bary = tk.Scrollbar(self.label7)
                self.bary.grid(row=0, column=1, sticky=N+S+E+W)
                self.ConList.config(yscrollcommand=self.bary.set)
                self.bary.config(command=self.ConList.yview)
                self.barx = tk.Scrollbar(self.label7, orient=HORIZONTAL)
                self.barx.grid(row=1, column=0, sticky=N+S+E+W)
                self.barx.config(command=self.ConList.xview)
                self.ConList.config(xscrollcommand=self.barx.set)


                sw = {}
                topo = self.net.topo.links()

                switches = 1
                shortedTopo = sorted(topo, key=lambda tup: int(tup[0][1:]))
                for i in range(int(self.Depth.get())-1):
                    switches = switches + pow(int(self.Fanout.get()),i+1)
                for i in range(switches):
                    sw[f's{i + 1}'] = ''

                for key, values in sw.items():
                    v = ''
                    for T in shortedTopo:
                        s, h = T
                        if key == s:
                            v = v + ' ' + h
                            sw[key] = v
                for key, value in sw.items():
                    self.ConList.insert(i,f'{key} : {value}')
                    # print(f"{key}: {values}\n")

            elif self.answer.get() == 'LinearTopo':
                self.next['state'] = DISABLED
                self.pre['state'] = DISABLED
                self.ConTable.destroy()
                self.ConList = tk.Listbox(self.label7, font = 'Calibri 25', height=6, width=22)
                self.ConList.grid(row=0, column=0)
                self.bary = tk.Scrollbar(self.label7)
                self.bary.grid(row=0, column=1, sticky=N + S + E + W)
                self.ConList.config(yscrollcommand=self.bary.set)
                self.bary.config(command=self.ConList.yview)
                self.barx = tk.Scrollbar(self.label7, orient=HORIZONTAL)
                self.barx.grid(row=1, column=0, sticky=N + S + E + W)
                self.barx.config(command=self.ConList.xview)
                self.ConList.config(xscrollcommand=self.barx.set)
                sw = {}
                topo = self.net.topo.links()

                shortedTopo = sorted(topo, key=lambda tup: int(tup[1][1:]))

                for i in range(int(self.Switches.get())):
                    sw[f's{i + 1}'] = ''
                for key, values in sw.items():
                    v = ''
                    for T in shortedTopo:
                        s, h = T
                        if key == h:
                            v = v + ' ' + s
                            sw[key] = v
                for key, value in sw.items():
                    self.ConList.insert(i,f'{key} : {value}')

            elif self.answer.get() == 'SingleTopo':
                totalhosts = int(self.PDCs.get())+int(self.PMUs.get())
                self.ConTable.destroy()
                self.ConList = tk.Listbox(self.label7,font = 'Calibri 25', height=6, width=22)
                self.ConList.grid(row=0, column=0)
                self.bary = tk.Scrollbar(self.label7)
                self.bary.grid(row=0, column=1, sticky=N + S + E + W)
                self.ConList.config(yscrollcommand=self.bary.set)
                self.bary.config(command=self.ConList.yview)
                self.barx = tk.Scrollbar(self.label7, orient=HORIZONTAL)
                self.barx.grid(row=1, column=0, sticky=N + S + E + W)
                self.barx.config(command=self.ConList.xview)
                self.ConList.config(xscrollcommand=self.barx.set)
                topo = self.net.hosts
                links = []
                for i in range(totalhosts):
                    links.append('s1')
                i = 0
                for h in self.net.hosts:
                    links[i] = f's1:{h}'
                    i+=1

                for i in range(len(links)):
                    switch, host = links[i].split(':')
                    self.ConList.insert(i, f'{switch} : {host}')


            elif self.answer.get() == 'MinimalTopo':
                self.ConTable.destroy()
                self.ConList = tk.Listbox(self.label7, font = 'Calibri 25', height=6, width=22)
                self.ConList.grid(row=0, column=0)
                self.bary = tk.Scrollbar(self.label7)
                self.bary.grid(row=0, column=1, sticky=N + S + E + W)
                self.ConList.config(yscrollcommand=self.bary.set)
                self.bary.config(command=self.ConList.yview)
                self.barx = tk.Scrollbar(self.label7, orient=HORIZONTAL)
                self.barx.grid(row=1, column=0, sticky=N + S + E + W)
                self.barx.config(command=self.ConList.xview)
                self.ConList.config(xscrollcommand=self.barx.set)
                self.ConList.insert(0,f's1:PDC1')
                self.ConList.insert(1, f's1:PMU1')

    def openController(self):
        print('Start Controller')
        os.system('ryu-manager ../../ryu/ryu/app/simple_switch.py')

    def startTopo(self): ##Εκκινηση του δικτυου
        # print("Hello")
        totalHosts = int(self.PMUs.get()) + int(self.PDCs.get())
        ans = self.answer.get()
        self.RunTopoFlag = True
        if ans == 'TreeTopo':
            # topo = CreateTopo(self.text1,self.text2)
            self.net = TreeNet(
            depth=int(self.Depth.get()), fanout=int(self.Fanout.get()), PMU = int(self.PMUs.get()), PDC = int(self.PDCs.get()),
            controller=RemoteController('c', ip='127.0.0.1'),  #controller=lambda name: Controller(name, ip='127.0.0.1')
            switch=OVSSwitch,
            autoSetMacs=True)
            self.y = threading.Thread(target=self.updateIpFrame)
            self.y.start()
            self.net.start()
            # CLI(self.net)


        elif ans == 'LinearTopo':
            switches = int(self.Switches.get())
            HostPerSwitch = int(self.HostPerSwitch.get())
            topo = LinearTopo(int(self.Switches.get()),int(self.HostPerSwitch.get()),PDC = int(self.PDCs.get()), PMU = int(self.PMUs.get()))
            self.net = Mininet(
                    topo=topo,
                    controller=RemoteController('c', ip='127.0.0.1'),
                    switch=OVSSwitch,
                    autoSetMacs=True)
            self.y = threading.Thread(target=self.updateIpFrame)
            self.y.start()
            self.net.start()



        elif ans == 'SingleTopo':
            Pmu = int(self.PMUs.get())
            Pdc = int(self.PDCs.get())
            topo = SingleSwitchTopo(totalHosts, PMU = Pmu, PDC = Pdc)
            self.net = Mininet(
                topo=topo,
                controller=RemoteController('c', ip='127.0.0.1'),
                switch=OVSSwitch,
                autoSetMacs=True)
            self.y = threading.Thread(target=self.updateIpFrame)
            self.y.start()
            self.net.start()



        elif ans == 'MinimalTopo':
            topo = MinimalTopoNew()
            self.net = Mininet(
                topo=topo,
                controller=RemoteController('c', ip='127.0.0.1'),
                switch=OVSSwitch,
                autoSetMacs=True)
            self.y = threading.Thread(target=self.updateIpFrame)
            self.y.start()
            self.net.start()
            # CLI(self.net)

        # p = Process(target=self.openController)
        # p.start()
        # p.join()


    def exit(self):
        self.net.stop()
        for child in self.root.winfo_children():
            # print(f'Children:{child}')
            child.destroy()
        App(root)


    def open_Streaming(self):
        self.buttonPMU.config(state='disabled')
        NewWindow(self.root, self.net,self.PmuStreamList,  self.PdcStreamList, self.Stats, self.buttonPMU)

    def close(self):
        self.window.destroy()
        self.buttonPMU.config(state = 'normal')






if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
