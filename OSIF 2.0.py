# python 3 tkinter import section

from tkinter import *
import tkinter as Tkinter
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox

# end python 3 tkinter import section


# python 2 Tkinter import section
'''
from Tkinter import *
import Tkinter
import tkFileDialog
import tkMessageBox
'''
# end python 2 Tkinter import section


import matplotlib
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec  # Allows for custom positioning of sub plots in matlibplot.
import scipy.optimize

# from default python modules
import os
import re
import webbrowser
import sys


def import_xlsx_file(path):
    """Read impedance data from an Excel file.

    Parameters
    ----------
    path : str
        Full path to the Excel file.

    Returns
    -------
    tuple of lists
        frequency, z_prime, z_double_prime, z_mod extracted from the file.
    """
    df = pd.read_excel(path)
    if "-Z'' (Ω)" in df.columns:
        df["Z'' (Ω)"] = -df.pop("-Z'' (Ω)")

    freq = df.iloc[:, 1].tolist()
    z_prime = df.iloc[:, 2].tolist()
    z_double = df.iloc[:, 3].tolist()
    z_mod = df.iloc[:, 4].tolist()
    return freq, z_prime, z_double, z_mod

# output pretty title, version info and citation prompt.
print('\n\n\n#########################################################################')
print('python version: ' + sys.version)
print('Tkinter version: ' + str(Tkinter.TkVersion))
print('#########################################################################\n\n')
print('############################################################')
print('#####     Open Source Impedance Fitter (OSIF) v2.0    #####')
print('############################################################')
print(
    "--------------------------\nWritten by Jason Pfeilsticker for the Hydrogen fuel cell manufacturing group\nat the National Renewable Energy Lab (NREL). Feb, 2018\nV2.0 adapted Oct. 2021\nCode for additional model options provided by Timothy Van cleve (NREL)")
print(
    '\nthis program uses the matplotlib, scipy, and numpy modules and was written in python.\nIf you publish data from this program, please cite them appropriately.\n'
    'To cite this code specifically, please cite the OSIF github page at: https://github.com/NREL/OSIF\n--------------------------\n\n\n')


# Main program class which is called on in line 868-ish to run the program.
class OSIF:

    def __init__(self, master):
        master.title("Open Source Impedance Fitter (OSIF) v1.25")
        master.grid()
        buttonFrame = Frame(master, pady=10, )
        InputFrame = Frame(master, padx=10)
        OutputFrame = Frame(master, padx=10)
        self.plotFrame = Frame(master, bg='blue')
        self.plotFrameToolBar = Frame(master, bg='red')

        Grid.grid_columnconfigure(buttonFrame, 0, weight=1)
        Grid.grid_rowconfigure(buttonFrame, 0, weight=1)
        Grid.grid_columnconfigure(self.plotFrame, 0, weight=1)
        Grid.grid_rowconfigure(self.plotFrame, 0, weight=1)
        Grid.grid_columnconfigure(self.plotFrameToolBar, 0, weight=1)
        Grid.grid_rowconfigure(self.plotFrameToolBar, 0, weight=1)

        buttonFrame.grid(row=0, columnspan=2)
        InputFrame.grid(row=1, column=0, sticky=N, pady=3)
        OutputFrame.grid(row=1, column=1, sticky=N, pady=3)
        self.plotFrame.grid(row=2, pady=1, padx=8, columnspan=5, sticky=N + S + E + W)
        self.plotFrameToolBar.grid(row=3, pady=1, padx=8, columnspan=5, sticky=S + W)

        self.Rmem = Param()
        self.Rcl = Param()
        self.Qdl = Param()
        self.Phi = Param()
        self.Lwire = Param()
        self.Theta = Param()
        self.area = Param()
        self.frequencyRange = Param()
        self.loading = Param()
        self.currentDataDir = Param()
        self.currentFileName = Tkinter.StringVar(master)
        self.model_selection = Tkinter.StringVar(master)
        self.currentFile = NONE
        self.avgResPer = Param()
        self.activeData = Data()

        entryFont = ("Calibri", '12')
        labelFont = ("Calibri", "12")

        sdPerColumn = 5
        sdColumn = 4
        fitValueColumn = 3
        unitColumn = 2
        nonFitUnitColumn = 2
        initValueColumn = 1
        varNameColumn = 0

        Label(InputFrame, text="Initial Values", font=labelFont).grid(row=1, column=initValueColumn, sticky=W)
        Label(OutputFrame, text="Fit Values", font=labelFont).grid(row=1, column=fitValueColumn, sticky=W)
        Label(OutputFrame, text="Estimated SE", font=labelFont).grid(row=1, column=sdColumn, sticky=W)
        Label(OutputFrame, text="SE % of fit value", font=labelFont).grid(row=1, column=sdPerColumn, sticky=W)

        ################################################
        ############ INPUT INITIAL VALUES ##############
        ################################################

        Label(InputFrame, text="Rmem:", font=labelFont).grid(row=2, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[ohm*cm^2]", font=labelFont).grid(row=2, column=unitColumn, sticky=W)
        self.Rmem.IE = Entry(InputFrame, width=10, font=entryFont)
        self.Rmem.IE.grid(row=2, column=initValueColumn)
        self.Rmem.IE.insert(0, "0.03")

        Label(InputFrame, text="Rcl:", font=labelFont).grid(row=3, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[ohm*cm^2]", font=labelFont).grid(row=3, column=unitColumn, sticky=W)
        self.Rcl.IE = Entry(InputFrame, width=10, font=entryFont)
        self.Rcl.IE.grid(row=3, column=initValueColumn)
        self.Rcl.IE.insert(0, "0.1")

        Label(InputFrame, text="Qdl:", font=labelFont).grid(row=4, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[F/(cm^2*sec^phi)]", font=labelFont).grid(row=4, column=unitColumn, sticky=W)
        self.Qdl.IE = Entry(InputFrame, width=10, font=entryFont)
        self.Qdl.IE.grid(row=4, column=initValueColumn)
        self.Qdl.IE.insert(0, "2.5")

        Label(InputFrame, text="Phi:", font=labelFont).grid(row=5, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[ - ]", font=labelFont).grid(row=5, column=unitColumn, sticky=W)
        self.Phi.IE = Entry(InputFrame, width=10, font=entryFont)
        self.Phi.IE.grid(row=5, column=initValueColumn)
        self.Phi.IE.insert(0, "0.95")

        Label(InputFrame, text="Lwire:", font=labelFont).grid(row=6, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[H*cm^2]", font=labelFont).grid(row=6, column=unitColumn, sticky=W)
        self.Lwire.IE = Entry(InputFrame, width=10, font=entryFont)
        self.Lwire.IE.grid(row=6, column=initValueColumn)
        self.Lwire.IE.insert(0, "2E-5")

        Label(InputFrame, text="Theta:", font=labelFont).grid(row=7, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[ - ]", font=labelFont).grid(row=7, column=unitColumn, sticky=W)
        self.Theta.IE = Entry(InputFrame, width=10, font=entryFont)
        self.Theta.IE.grid(row=7, column=initValueColumn)
        self.Theta.IE.insert(0, "0.95")

        Label(InputFrame, text="Cell Area:", font=labelFont).grid(row=8, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[cm^2]", font=labelFont).grid(row=8, column=nonFitUnitColumn, sticky=W)
        self.area.IE = Entry(InputFrame, width=10, font=entryFont)
        self.area.IE.grid(row=8, column=initValueColumn)
        self.area.IE.insert(0, "50")

        Label(InputFrame, text="catalyst loading:", font=labelFont).grid(row=9, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[mg/cm^2]", font=labelFont).grid(row=9, column=nonFitUnitColumn, sticky=W)
        self.loading.IE = Entry(InputFrame, width=10, font=entryFont)
        self.loading.IE.grid(row=9, column=initValueColumn)
        self.loading.IE.insert(0, "0.1")

        Label(InputFrame, text="upper Frequency bound:", font=labelFont).grid(row=10, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[Hz]", font=labelFont).grid(row=10, column=nonFitUnitColumn, sticky=W)
        self.frequencyRange.IE = Entry(InputFrame, width=10, font=entryFont)
        self.frequencyRange.IE.grid(row=10, column=initValueColumn)
        self.frequencyRange.IE.insert(0, "10000")

        Label(InputFrame, text="lower Frequency bound:", font=labelFont).grid(row=11, column=varNameColumn, sticky=E)
        Label(InputFrame, text="[Hz]", font=labelFont).grid(row=11, column=nonFitUnitColumn, sticky=W)
        self.frequencyRange.OE = Entry(InputFrame, width=10, font=entryFont)
        self.frequencyRange.OE.grid(row=11, column=initValueColumn)
        self.frequencyRange.OE.insert(0, "1")

        ################################################
        ########### OUTPUT VALUES FROM FIT #############
        ################################################
        ioBoxWidth = 10
        self.Rmem.OE = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Rmem.OE.grid(row=2, column=fitValueColumn, sticky=W)
        self.Rmem.OE.insert(0, "---")
        self.Rmem.OE.config(state='readonly')

        self.Rcl.OE = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Rcl.OE.grid(row=3, column=fitValueColumn, sticky=W)
        self.Rcl.OE.insert(0, "---")
        self.Rcl.OE.config(state='readonly')

        self.Qdl.OE = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Qdl.OE.grid(row=4, column=fitValueColumn, sticky=W)
        self.Qdl.OE.insert(0, "---")
        self.Qdl.OE.config(state='readonly')

        self.Phi.OE = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Phi.OE.grid(row=5, column=fitValueColumn, sticky=W)
        self.Phi.OE.insert(0, "---")
        self.Phi.OE.config(state='readonly')

        self.Lwire.OE = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Lwire.OE.grid(row=6, column=fitValueColumn, sticky=W)
        self.Lwire.OE.insert(0, "---")
        self.Lwire.OE.config(state='readonly')

        self.Theta.OE = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Theta.OE.grid(row=7, column=fitValueColumn, sticky=W)
        self.Theta.OE.insert(0, "---")
        self.Theta.OE.config(state='readonly')

        ################################################
        ########### OUTPUT VALUE SD values #############
        ################################################

        self.Rmem.OESD = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Rmem.OESD.grid(row=2, column=sdColumn, sticky=W)
        self.Rmem.OESD.insert(0, "---")
        self.Rmem.OESD.config(state='readonly')

        self.Rcl.OESD = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Rcl.OESD.grid(row=3, column=sdColumn, sticky=W)
        self.Rcl.OESD.insert(0, "---")
        self.Rcl.OESD.config(state='readonly')

        self.Qdl.OESD = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Qdl.OESD.grid(row=4, column=sdColumn, sticky=W)
        self.Qdl.OESD.insert(0, "---")
        self.Qdl.OESD.config(state='readonly')

        self.Phi.OESD = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Phi.OESD.grid(row=5, column=sdColumn, sticky=W)
        self.Phi.OESD.insert(0, "---")
        self.Phi.OESD.config(state='readonly')

        self.Lwire.OESD = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Lwire.OESD.grid(row=6, column=sdColumn, sticky=W)
        self.Lwire.OESD.insert(0, "---")
        self.Lwire.OESD.config(state='readonly')

        self.Theta.OESD = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Theta.OESD.grid(row=7, column=sdColumn, sticky=W)
        self.Theta.OESD.insert(0, "---")
        self.Theta.OESD.config(state='readonly')

        ################################################
        ############ OUTPUT SD % OF VALUES #############
        ################################################

        self.Rmem.OESDP = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Rmem.OESDP.grid(row=2, column=sdPerColumn, sticky=W)
        self.Rmem.OESDP.insert(0, "---")
        self.Rmem.OESDP.config(state='readonly')

        self.Rcl.OESDP = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Rcl.OESDP.grid(row=3, column=sdPerColumn, sticky=W)
        self.Rcl.OESDP.insert(0, "---")
        self.Rcl.OESDP.config(state='readonly')

        self.Qdl.OESDP = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Qdl.OESDP.grid(row=4, column=sdPerColumn, sticky=W)
        self.Qdl.OESDP.insert(0, "---")
        self.Qdl.OESDP.config(state='readonly')

        self.Phi.OESDP = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Phi.OESDP.grid(row=5, column=sdPerColumn, sticky=W)
        self.Phi.OESDP.insert(0, "---")
        self.Phi.OESDP.config(state='readonly')

        self.Lwire.OESDP = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Lwire.OESDP.grid(row=6, column=sdPerColumn, sticky=W)
        self.Lwire.OESDP.insert(0, "---")
        self.Lwire.OESDP.config(state='readonly')

        self.Theta.OESDP = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.Theta.OESDP.grid(row=7, column=sdPerColumn, sticky=W)
        self.Theta.OESDP.insert(0, "---")
        self.Theta.OESDP.config(state='readonly')

        ################################################
        ########## OUTPUT AVG RES |Z| VALUE ############
        ################################################

        Label(OutputFrame, text="Avg. |Z| residual % of data |Z|:", font=labelFont).grid(row=9,
                                                                                         column=(sdPerColumn - 2),
                                                                                         columnspan=2, pady=20,
                                                                                         sticky=E)
        self.avgResPer.AVGRESPER = Entry(OutputFrame, width=ioBoxWidth, font=entryFont)
        self.avgResPer.AVGRESPER.grid(row=9, column=sdPerColumn, sticky=W)
        self.avgResPer.AVGRESPER.insert(0, "---")
        self.avgResPer.AVGRESPER.config(state='readonly')

        ################################################
        #################### BUTTONS ###################
        ################################################

        self.simB = Button(buttonFrame, text="Select Data Directory", command=lambda: self.SelectDataDir())
        self.simB.grid(row=0, column=0, sticky=E)

        self.simB = Button(buttonFrame, text="Model Info.", command=self.openModelInfo)
        self.simB.grid(row=0, column=1, sticky=E)

        self.simB = Button(buttonFrame, text="Citation Info.", command=self.openCitationInfo)
        self.simB.grid(row=0, column=2, sticky=W)

        self.fitB = Button(buttonFrame, text="Fit", command=self.PerformFit)
        self.fitB.grid(row=0, column=3, sticky=E)

        self.simB = Button(buttonFrame, text="Simulate", command=self.PerformSim)
        self.simB.grid(row=0, column=4, sticky=W)

        self.simB = Button(OutputFrame, text="Save Model Data", command=self.SaveData)
        self.simB.grid(row=9, column=sdPerColumn - 2, columnspan=3, sticky=N)

        Label(buttonFrame, text="Current Directory:", font=labelFont).grid(row=1, column=0, sticky=E)
        self.currentDataDir.IE = Entry(buttonFrame, width=60, font=entryFont)
        self.currentDataDir.IE.grid(row=1, column=1, sticky=W, columnspan=2)
        self.currentDataDir.IE.insert(0, "---")
        self.currentDataDir.IE.config(state='readonly')

        Label(buttonFrame, text="Current Data File:", font=labelFont).grid(row=2, column=0, sticky=E)
        self.choices = ['Data Directory not selected']
        self.fileSelectComboBox = OptionMenu(buttonFrame, self.currentFileName, *self.choices)
        self.fileSelectComboBox.grid(row=2, column=1, sticky=EW, columnspan=2)
        self.fileSelectComboBox.config(font=entryFont)

        Label(buttonFrame, text="Select Circuit Model:", font=labelFont).grid(row=3, column=0, sticky=E)
        self.eis_model = ["Transmission Line", "1-D Linear Diffusion", "1-D Spherical Diffusion"]
        self.model_selection.set(self.eis_model[0])
        self.fileSelectModelBox = OptionMenu(buttonFrame, self.model_selection, *self.eis_model)
        self.fileSelectModelBox.grid(row=3, column=1, sticky=EW, columnspan=2)
        self.fileSelectModelBox.config(font=entryFont)
        # self.fileSelectModelBox.pack()

    def openModelInfo(self):
        if self.model_selection.get() == self.eis_model[0]:
            print(
                "--------------------------\nThe model being used in this program is Eq. 2 from the opened Fuller paper.\nThe derivation can be found in their suplimentary information. If you would\nlike to use a different model, contact Jason Pfeilsticker.\n\n")
            webbrowser.open("https://iopscience.iop.org/article/10.1149/2.0361506jes")
        elif self.model_selection.get() == self.eis_model[1]:
            print("1-D linear diffusion model selected.")
            webbrowser.open("https://www.researchgate.net/publication/342833389_Handbook_of_Electrochemical_Impedance_Spectroscopy_DIFFUSION_IMPEDANCES")
        elif self.model_selection.get() == self.eis_model[2]:
            print("1-D spherical diffusion model selected.")
            webbrowser.open("https://www.researchgate.net/publication/342833389_Handbook_of_Electrochemical_Impedance_Spectroscopy_DIFFUSION_IMPEDANCES")





    def openCitationInfo(self):
        print(
            "--------------------------\nThe Program uses the the matplotlib, scipy, and numpy modules and was written in\n"
            "python (Scientific Computing in Python). Please cite them accordingly via the opend website\n"
            "To cite this code specifically please cite the OSIF github repository")
        webbrowser.open("https://www.scipy.org/citing.html")
        webbrowser.open("https://github.com/NREL/OSIF")

    def SelectDataDir(self):
        newDir = tkFileDialog.askdirectory(title="Select EIS data directory") + '/'
        self.currentDataDir.IE.config(state='normal')
        self.currentDataDir.IE.delete(0, END)
        self.currentDataDir.IE.insert(0, newDir)
        self.currentDataDir.IE.config(state='readonly')

        dirList = os.listdir(newDir)
        dirList = [dataFile for dataFile in dirList if
                   ('.txt' in dataFile) | ('.xls' in dataFile) | ('.xlsx' in dataFile)]
        self.fileSelectComboBox.configure(state='normal')  # Enable drop down
        menu = self.fileSelectComboBox.children['menu']

        # Clear the menu.
        menu.delete(0, 'end')
        for file in dirList:
            # Add menu items.
            menu.add_command(label=file, command=lambda v=self.currentFileName, l=file: v.set(l))
        print('Selected Data Directory: ' + self.currentDataDir.IE.get())

    def load_selected_file(self):
        if not self.currentFileName.get() or self.currentFileName.get() == '---':
            print('attempt to load on null selection')
            return

        print("\n===========================================\n  loading file: " + self.currentFileName.get() + '\n===========================================\n\n')

        self.activeData.rawFrequency = []
        self.activeData.rawzPrime = []
        self.activeData.rawZdoublePrime = []
        self.activeData.rawzMod = []
        self.activeData.rawZExperimentalComplex = []
        self.activeData.rawmodZExperimentalComplex = []

        self.activeData.dataName = self.currentFileName.get()
        self.activeData.dataNameNoExt = Path(self.activeData.dataName).stem

        file_path = os.path.join(self.currentDataDir.IE.get(), self.currentFileName.get())

        try:
            if file_path.endswith('.txt'):
                df = pd.read_csv(file_path, sep='\t', comment='#')
                if "-Z'' (Ω)" in df.columns:
                    df["Z'' (Ω)"] = -df.pop("-Z'' (Ω)")

                self.activeData.rawFrequency = df.iloc[:, 1].to_numpy()
                self.activeData.rawzPrime = df.iloc[:, 2].to_numpy()
                self.activeData.rawZdoublePrime = df.iloc[:, 3].to_numpy()
                self.activeData.rawzMod = df.iloc[:, 4].to_numpy()
            else:
                (self.activeData.rawFrequency,
                 self.activeData.rawzPrime,
                 self.activeData.rawZdoublePrime,
                 self.activeData.rawzMod) = (
                    np.array(v) for v in import_xlsx_file(file_path))
        except Exception as e:
            tkMessageBox.showinfo('Error!', f'Failed to read data file: {e}')
            return

        self.activeData.rawZExperimentalComplex = (
            self.activeData.rawzPrime + 1j * self.activeData.rawZdoublePrime)
        self.activeData.rawmodZExperimentalComplex = np.abs(self.activeData.rawZExperimentalComplex)

        print('\n\tFrequency,\t\tRe(Z),\t\t\tIm(Z),\t\t\t\t|Z|')
        for f, r, i, m in zip(self.activeData.rawFrequency, self.activeData.rawzPrime,
                              self.activeData.rawZdoublePrime, self.activeData.rawzMod):
            print(f, r, i, m)

        self.activeData.rawFrequency = np.array(self.activeData.rawFrequency)
        self.activeData.rawPhase = (180 / np.pi) * np.arctan(
            self.activeData.rawZdoublePrime / self.activeData.rawzPrime)

        print(len(self.activeData.rawPhase), len(self.activeData.rawzMod))
        print("===============================\ndone loading file\n==========================")

    def ChopFreq(self):
        tempFreq = []
        self.activeData.frequency = np.array([])
        for freq in self.activeData.rawFrequency:
            if (freq > float(self.frequencyRange.OE.get())) & (freq < float(self.frequencyRange.IE.get())):
                tempFreq.append(freq)

        # chop the data to the frequency range specified in set up
        self.activeData.frequency = np.array(tempFreq)
        minIndex = self.activeData.rawFrequency.tolist().index(self.activeData.frequency[0])
        maxIndex = self.activeData.rawFrequency.tolist().index(
            self.activeData.frequency[self.activeData.frequency.shape[0] - 1])

        self.activeData.zPrime = self.activeData.rawzPrime[minIndex:maxIndex + 1]
        self.activeData.ZdoublePrime = self.activeData.rawZdoublePrime[minIndex:maxIndex + 1]
        self.activeData.zMod = self.activeData.rawzMod[minIndex:maxIndex + 1]
        self.activeData.modZExperimentalComplex = self.activeData.rawmodZExperimentalComplex[minIndex:maxIndex + 1]
        self.activeData.phase = self.activeData.rawPhase[minIndex:maxIndex + 1]

    def PerformSim(self):
        self.load_selected_file()
        if len(self.activeData.rawzPrime) == 0:
            tkMessageBox.showinfo("Error!", "No data file loaded\nor data is in incorrect format")
            return

        else:
            self.ChopFreq()
            ###### /float(self.area.IE.get())      Rmem
            params = [float(self.Lwire.IE.get()) / float(self.area.IE.get()),
                      float(self.Rmem.IE.get()) / float(self.area.IE.get()),
                      float(self.Rcl.IE.get()) / float(self.area.IE.get()),
                      float(self.Qdl.IE.get()),
                      float(self.Phi.IE.get()),
                      float(self.Theta.IE.get())]

            self.CreateFigures(params, 'sim')

            print("Model Selection Made:", self.model_selection.get())
            simResiduals = self.funcCost(params)
            # print simResiduals.get()
            self.resPercentData = np.sum(simResiduals / self.activeData.zMod * 100) / len(simResiduals)
            self.avgResPer.AVGRESPER.config(state='normal')
            self.avgResPer.AVGRESPER.delete(0, END)
            self.avgResPer.AVGRESPER.insert(0, '%5.4f' % self.resPercentData)
            self.avgResPer.AVGRESPER.config(state='readonly')

    def PerformFit(self):
        self.load_selected_file()
        print('\n\n\n\n' + 'Sample: ' + self.currentFileName.get() + '\n')
        if len(self.activeData.rawzPrime) == 0:
            tkMessageBox.showinfo("Error!", "No data file loaded\nor data is in incorrect format")
            return

        else:
            ### /float(self.area.IE.get())   Rmem
            self.ChopFreq()

            # Estimate Rmem directly from the data.  When the imaginary
            # component of the impedance is approximately zero, the real
            # component corresponds to the membrane resistance.  The data
            # arrays are chopped to the frequency range at this point, so we
            # simply find the value of Z' where |Z''| is minimal.
            idx_rmem = int(np.argmin(np.abs(self.activeData.ZdoublePrime)))
            est_rmem = self.activeData.zPrime[idx_rmem]

            # Update the GUI with the estimated Rmem in [ohm*cm^2]
            self.Rmem.IE.delete(0, END)
            self.Rmem.IE.insert(0, '%5.8f' % (est_rmem * float(self.area.IE.get())))

            params = [float(self.Lwire.IE.get()) / float(self.area.IE.get()),
                      float(self.Rmem.IE.get()) / float(self.area.IE.get()),
                      float(self.Rcl.IE.get()) / float(self.area.IE.get()),
                      float(self.Qdl.IE.get()),
                      float(self.Phi.IE.get()),
                      float(self.Theta.IE.get())]

            # Perform the fitting using least_squares with the TRF method and max function calls of 10000.
            rmem_param = float(self.Rmem.IE.get()) / float(self.area.IE.get())
            bounds_lower = (0, 0.9 * rmem_param, 0, 0, 0, 0)
            bounds_upper = (1, 1.1 * rmem_param, np.inf, np.inf, 1, 1)

            finalOutput = scipy.optimize.least_squares(self.funcCost, params,
                                                       bounds=[bounds_lower, bounds_upper],
                                                       max_nfev=50000, method='trf', xtol=1e-11,
                                                       ftol=1e-11, gtol=1e-11, verbose=1)
            self.finalParams = finalOutput.x

            # Estimate variance of parameters based on Gauss-Newton approximation of the Hessian of the cost function. See: (https://www8.cs.umu.se/kurser/5DA001/HT07/lectures/lsq-handouts.pdf)
            # basically Covariance matrix = inverse(Jacob^T*Jacob)*meanSquaredError, where Jacob^T*Jacob is the first order estimate for the hessian. The square root of the diagonal elements (c_ii) of Cov are the variances of the parameter b_i

            # sigma squared estimate also called s^2 sometimes = chi^2 reduced
            sigmaSquared = (np.matmul(np.transpose(finalOutput.fun), finalOutput.fun)) / (
                    finalOutput.fun.shape[0] - self.finalParams.size)

            # Plot residuals for error checking. Note: cancels update of the normal plots in the normal UI.
            # plt.figure(100)
            # plt.plot(finalOutput.fun)
            # plt.show()

            Jacob = finalOutput.jac
            estVars = np.matrix.diagonal(
                np.linalg.inv(Jacob.T.dot(Jacob)) * (np.matmul(np.transpose(finalOutput.fun), finalOutput.fun)) / (
                        finalOutput.fun.shape[0] - self.finalParams.size))
            # estVars = sigmaSquared*np.matrix.diagonal(np.linalg.inv(np.matmul(np.matrix.transpose(finalOutput.jac),finalOutput.jac)))

            # estimated errors in parameters
            self.standardDeviation = np.sqrt(estVars)

            # taking chi^2  = sum((residuals^T)*(residuals)) = sum (r_i)^2
            # print('Sum res^2 = ' + str(np.sum((np.matrix.transpose(finalOutput.fun).__mul__(finalOutput.fun)))))

            self.L2NormOfRes = np.sqrt(np.sum(pow(finalOutput.fun, 2)))

            # print('\nNormalized grad = grad/|grad| = ' + str(finalOutput.grad / np.sqrt(np.sum(pow(finalOutput.grad, 2)))))

            self.resPercentData = np.sum(finalOutput.fun / self.activeData.zMod * 100) / finalOutput.fun.shape[0]

            print('\nFit to: ' + self.activeData.dataNameNoExt)

            self.percentSigma = self.standardDeviation / self.finalParams * 100

            self.fitOutPutString = '#\n#\n#\t\t\t\t\t\t\t   Fit values\t\t\t~std Error\t\t\t ~std Error %% of value\n#\n#\tRmem  [ohm*cm^2] \t\t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\tRcl   [ohm*cm^2] \t\t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f' \
                                   '\n#\tQdl   [F/(sec^phi)]  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\tphi   [ ]  \t\t\t\t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\tLwire [H*cm^2] \t\t\t  = %.4e\t\t\t%.3e\t\t\t\t%8.2f' \
                                   '\n#\tphi   [ ]  \t\t\t\t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\n#\tQdl/mgpt = %5.6f\n#\tL2 norm of res = %10.8f [ohm*cm^2]' % \
                                   (float(self.finalParams[1]) * float(self.area.IE.get()),
                                    float(self.standardDeviation[1]) * float(self.area.IE.get()), self.percentSigma[1],
                                    float(self.finalParams[2]) * float(self.area.IE.get()),
                                    float(self.standardDeviation[2]) * float(self.area.IE.get()), self.percentSigma[2],
                                    float(self.finalParams[3]), float(self.standardDeviation[3]), self.percentSigma[3],
                                    float(self.finalParams[4]), float(self.standardDeviation[4]), self.percentSigma[4],
                                    float(self.finalParams[0]) * float(self.area.IE.get()),
                                    float(self.standardDeviation[0]) * float(self.area.IE.get()), self.percentSigma[0],
                                    float(self.finalParams[5]), float(self.standardDeviation[5]), self.percentSigma[5],
                                    float(self.finalParams[3]) / (
                                                float(self.area.IE.get()) * float(self.loading.IE.get())),
                                    float(self.L2NormOfRes) * float(self.area.IE.get()))

            print(self.fitOutPutString)
            if self.model_selection.get() == self.eis_model[0]:
                self.realFinalModel = self.funcreal(self.finalParams)
                self.imagFinalModel = self.funcImg(self.finalParams)
            elif self.model_selection.get() == self.eis_model[1]:
                self.realFinalModel = self.funcreal_l(self.finalParams)
                self.imagFinalModel = self.funcImg_l(self.finalParams)
            elif self.model_selection.get() == self.eis_model[2]:
                self.realFinalModel = self.funcreal_s(self.finalParams)
                self.imagFinalModel = self.funcImg_s(self.finalParams)
            self.zModFinalModel = self.funcAbs(self.finalParams)
            self.phaseFinalModel = self.funcPhase(self.finalParams)
            # (180/(np.pi))*np.arctan(self.funcImg(self.finalParams)/self.funcreal(self.finalParams))

            self.AvgRealResPer = np.sum(abs(
                np.array(abs(self.realFinalModel - self.activeData.zPrime)) / np.array(self.activeData.zPrime)) * 100) / \
                                 self.realFinalModel.shape[0]
            self.AvgImagResPer = np.sum(abs(
                np.array(abs(self.imagFinalModel - self.activeData.ZdoublePrime)) / np.array(
                    self.activeData.ZdoublePrime)) * 100) / \
                                 self.imagFinalModel.shape[0]
            # print('\nAvgRealResPer = ' + str(self.AvgRealResPer) + '\nAvgImagResPer = ' + str(self.AvgImagResPer))

            self.Lwire.OE.config(state='normal')
            self.Lwire.OE.delete(0, END)
            self.Lwire.OE.insert(0, '%5.8f' % (float(self.finalParams[0]) * float(self.area.IE.get())))
            self.Lwire.OE.config(state='readonly')

            self.Rmem.OE.config(state='normal')
            self.Rmem.OE.delete(0, END)
            self.Rmem.OE.insert(0, '%5.8f' % (float(self.finalParams[1]) * float(self.area.IE.get())))
            self.Rmem.OE.config(state='readonly')

            self.Rcl.OE.config(state='normal')
            self.Rcl.OE.delete(0, END)
            self.Rcl.OE.insert(0, '%5.8f' % (self.finalParams[2] * float(self.area.IE.get())))
            self.Rcl.OE.config(state='readonly')

            self.Qdl.OE.config(state='normal')
            self.Qdl.OE.delete(0, END)
            self.Qdl.OE.insert(0, '%5.8f' % self.finalParams[3])
            self.Qdl.OE.config(state='readonly')

            self.Phi.OE.config(state='normal')
            self.Phi.OE.delete(0, END)
            self.Phi.OE.insert(0, '%5.8f' % self.finalParams[4])
            self.Phi.OE.config(state='readonly')

            self.Theta.OE.config(state='normal')
            self.Theta.OE.delete(0, END)
            self.Theta.OE.insert(0, '%5.8f' % self.finalParams[5])
            self.Theta.OE.config(state='readonly')

            self.Lwire.OESD.config(state='normal')
            self.Lwire.OESD.delete(0, END)
            self.Lwire.OESD.insert(0, '%5.8f' % (self.standardDeviation[0] * float(self.area.IE.get())))
            self.Lwire.OESD.config(state='readonly')

            self.Rmem.OESD.config(state='normal')
            self.Rmem.OESD.delete(0, END)
            self.Rmem.OESD.insert(0, '%5.8f' % ((float(self.standardDeviation[1]) * float(self.area.IE.get()))))
            self.Rmem.OESD.config(state='readonly')

            self.Rcl.OESD.config(state='normal')
            self.Rcl.OESD.delete(0, END)
            self.Rcl.OESD.insert(0, '%5.8f' % (self.standardDeviation[2] * float(self.area.IE.get())))
            self.Rcl.OESD.config(state='readonly')

            self.Qdl.OESD.config(state='normal')
            self.Qdl.OESD.delete(0, END)
            self.Qdl.OESD.insert(0, '%5.8f' % self.standardDeviation[3])
            self.Qdl.OESD.config(state='readonly')

            self.Phi.OESD.config(state='normal')
            self.Phi.OESD.delete(0, END)
            self.Phi.OESD.insert(0, '%5.8f' % self.standardDeviation[4])
            self.Phi.OESD.config(state='readonly')

            self.Theta.OESD.config(state='normal')
            self.Theta.OESD.delete(0, END)
            self.Theta.OESD.insert(0, '%5.8f' % self.standardDeviation[5])
            self.Theta.OESD.config(state='readonly')

            self.Lwire.OESDP.config(state='normal')
            self.Lwire.OESDP.delete(0, END)
            self.Lwire.OESDP.insert(0, '%5.4f' % (self.percentSigma[0]))
            self.Lwire.OESDP.config(state='readonly')

            self.Rmem.OESDP.config(state='normal')
            self.Rmem.OESDP.delete(0, END)
            self.Rmem.OESDP.insert(0, '%5.4f' % (self.percentSigma[1]))
            self.Rmem.OESDP.config(state='readonly')

            self.Rcl.OESDP.config(state='normal')
            self.Rcl.OESDP.delete(0, END)
            self.Rcl.OESDP.insert(0, '%5.4f' % (self.percentSigma[2]))
            self.Rcl.OESDP.config(state='readonly')

            self.Qdl.OESDP.config(state='normal')
            self.Qdl.OESDP.delete(0, END)
            self.Qdl.OESDP.insert(0, '%5.4f' % self.percentSigma[3])
            self.Qdl.OESDP.config(state='readonly')

            self.Phi.OESDP.config(state='normal')
            self.Phi.OESDP.delete(0, END)
            self.Phi.OESDP.insert(0, '%5.4f' % self.percentSigma[4])
            self.Phi.OESDP.config(state='readonly')

            self.Theta.OESDP.config(state='normal')
            self.Theta.OESDP.delete(0, END)
            self.Theta.OESDP.insert(0, '%5.4f' % self.percentSigma[5])
            self.Theta.OESDP.config(state='readonly')

            self.avgResPer.AVGRESPER.config(state='normal')
            self.avgResPer.AVGRESPER.delete(0, END)
            self.avgResPer.AVGRESPER.insert(0, '%5.4f' % self.resPercentData)
            self.avgResPer.AVGRESPER.config(state='readonly')

            self.CreateFigures(self.finalParams, 'fit')

    def CreateFigures(self, params, fitOrSim):
        if fitOrSim == 'fit':
            graphLabel = 'Full complex fit: '
        elif fitOrSim == 'sim':
            graphLabel = 'Simulated using: '
        else:
            graphLabel = ''

        plt.close('all')
        # make layout for graphs
        gs0 = gridspec.GridSpec(1, 2)
        gs00 = gridspec.GridSpecFromSubplotSpec(4, 3, subplot_spec=gs0[0])
        gs01 = gridspec.GridSpecFromSubplotSpec(4, 4, subplot_spec=gs0[1])
        f = plt.figure(1, figsize=[8, 3.5], tight_layout='true')

        ###########################################################
        ####          PLOT NYQUIST COMBINED FITTINGS           ####
        ###########################################################

        nyGraph = plt.Subplot(f, gs01[:, :])
        f.add_subplot(nyGraph)
        nyGraph.plot(self.activeData.zPrime, self.activeData.ZdoublePrime, 'bo', ls='--', markersize=2, linewidth=1,
                     label='data: ' + self.activeData.dataNameNoExt)

        if self.model_selection.get() == self.eis_model[0]:
            nyGraph.plot(self.funcreal(params), self.funcImg(params), 'ro', markersize=2,
                         label='\n%s\nLwire=%.5e\nRmem=%5.8f\nRcl=%5.8f\nQdl=%5.5f\nphi=%5.5f\ntheta=%5.5f' % (
                             graphLabel, params[0] * float(self.area.IE.get()), params[1] * float(self.area.IE.get()),
                             params[2] * float(self.area.IE.get()), params[3], params[4], params[5]))

        elif self.model_selection.get() == self.eis_model[1]:
            nyGraph.plot(self.funcreal_l(params), self.funcImg_l(params), 'ro', markersize=2,
                         label='\n%s\nLwire=%.5e\nRmem=%5.8f\nRcl=%5.8f\nQdl=%5.5f\nphi=%5.5f\ntheta=%5.5f' % (
                             graphLabel, params[0] * float(self.area.IE.get()), params[1] * float(self.area.IE.get()),
                             params[2] * float(self.area.IE.get()), params[3], params[4], params[5]))

        elif self.model_selection.get() == self.eis_model[2]:
            nyGraph.plot(self.funcreal_s(params), self.funcImg_s(params), 'ro', markersize=2,
                         label='\n%s\nLwire=%.5e\nRmem=%5.8f\nRcl=%5.8f\nQdl=%5.5f\nphi=%5.5f\ntheta=%5.5f' % (
                             graphLabel, params[0] * float(self.area.IE.get()), params[1] * float(self.area.IE.get()),
                             params[2] * float(self.area.IE.get()), params[3], params[4], params[5]))

        plt.gca().invert_yaxis()
        plt.xticks(rotation=20)

        plt.xlabel('Re(Z)')
        plt.ylabel('Im(Z)')
        plt.legend(loc=2, fontsize=6)

        ###########################################################
        ####        PLOT Phase vs w COMBINED FITTINGS          ####
        ###########################################################

        phaseGraph = plt.Subplot(f, gs00[-4, :3])
        f.add_subplot(phaseGraph)
        phaseGraph.plot(self.activeData.frequency, self.activeData.phase, 'bo', ls='--', markersize=2,
                        linewidth=1)
        phaseGraph.plot(self.activeData.frequency, self.funcPhase(params), 'ro', markersize=2)
        plt.ylabel('phase')
        # plt.gca().set_yscale('log')
        plt.gca().set_xscale('log')

        ###########################################################
        ####         PLOT |Z| vs w COMBINED FITTINGS           ####
        ###########################################################

        modZgraph = plt.Subplot(f, gs00[-3, :3])
        f.add_subplot(modZgraph)
        modZgraph.plot(self.activeData.frequency, self.activeData.modZExperimentalComplex, 'bo', ls='--', markersize=2,
                       linewidth=1)
        modZgraph.plot(self.activeData.frequency, self.funcAbs(params), 'ro', markersize=2)
        plt.ylabel('|Z|')
        plt.gca().set_yscale('log')
        plt.gca().set_xscale('log')

        ###########################################################
        ####                   PLOT Im(Z)                      ####
        ###########################################################

        imZgraph = plt.Subplot(f, gs00[-2, :3])
        f.add_subplot(imZgraph)
        imZgraph.plot(self.activeData.frequency, self.activeData.ZdoublePrime, 'bo', ls='--', markersize=2, linewidth=1)

        if self.model_selection.get() == self.eis_model[0]:
            imZgraph.plot(self.activeData.frequency, (self.funcImg(params)), 'ro', markersize=2)
        elif self.model_selection.get() == self.eis_model[1]:
            imZgraph.plot(self.activeData.frequency, (self.funcImg_l(params)), 'ro', markersize=2)
        elif self.model_selection.get() == self.eis_model[2]:
            imZgraph.plot(self.activeData.frequency, (self.funcImg_s(params)), 'ro', markersize=2)

        plt.ylabel('Im(Z)')
        plt.gca().set_yscale('linear')
        plt.gca().set_xscale('log')
        plt.gca().set_xticks([])

        ###########################################################
        ####                   PLOT Re(Z)                      ####
        ###########################################################

        reZgraph = plt.Subplot(f, gs00[-1, :3])
        f.add_subplot(reZgraph)
        reZgraph.plot(self.activeData.frequency, self.activeData.zPrime, 'bo', ls='--', markersize=2, linewidth=1)

        if self.model_selection.get() == self.eis_model[0]:
            reZgraph.plot(self.activeData.frequency, self.funcreal(params), 'ro', markersize=2)
        elif self.model_selection.get() == self.eis_model[1]:
            reZgraph.plot(self.activeData.frequency, (self.funcreal_l(params)), 'ro', markersize=2)
        elif self.model_selection.get() == self.eis_model[2]:
            reZgraph.plot(self.activeData.frequency, (self.funcreal_s(params)), 'ro', markersize=2)

        plt.xlabel('frequency')
        plt.ylabel('Re(Z)')
        plt.gca().set_yscale('log')
        plt.gca().set_xscale('log')

        ###########################################################
        ####              Draw figure in Tkinter               ####
        ###########################################################
        for widget in self.plotFrame.winfo_children():
            widget.destroy()
        for widget in self.plotFrameToolBar.winfo_children():
            widget.destroy()

        dataPlot = FigureCanvasTkAgg(f, master=self.plotFrame)
        dataPlot.close_event()
        dataPlot.draw()
        dataPlot.get_tk_widget().grid(row=0, sticky=N + S + E + W, )
        # toolbar = NavigationToolbar2TkAgg(dataPlot, self.plotFrameToolBar)
        # toolbar.update()
        dataPlot._tkcanvas.grid(row=0, sticky=W + S)

        print('done with plotting')

    def KILLALL(self):
        for widget in self.plotFrame.winfo_children():
            widget.destroy()
        #   for widget in self.plotFrameToolBar.winfo_children():
        #       widget.destroy()
        print("\n\nAll plots killed. \nHave a nice day!")

    def SaveData(self):
        if (len(self.currentFileName.get()) == 0) | (self.currentFileName.get() == '---'):
            print('no data loaded')
            tkMessageBox.showinfo("Error!", "No data file loaded")
            # nothing selected to load
            return

        dataOutFile = open(self.currentDataDir.IE.get() + self.activeData.dataNameNoExt + '_fit.txt', "w+")
        i = 0
        dataOutFile.write('#Fitted model at fitting frequencies:\n#Frequency\t\tRe(Z)\t\t\tIm(Z)\t\t\t|Z|\n')
        for real in self.realFinalModel:
            dataOutFile.write(
                str(self.activeData.frequency[i]) + '\t' + str(self.realFinalModel[i]) + '\t' + str(
                    self.imagFinalModel[i]) + '\t' + str(
                    self.zModFinalModel[i]) + '\n')
            i += 1

        dataOutFile.write(
            '#\n#\n#\t\t\t\t   Fit values\t\t\t~std dev\t\t\t   ~stdDev %% of value\n#\n#\tRmem  [ohm*cm^2] \t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\tRcl   [ohm*cm^2] \t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f' \
            '\n#\tQdl   [F/(cm^2*sec^phi)]  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\tphi   [ ]  \t\t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\tLwire [H*cm^2] \t\t  = %.4e\t\t\t%.3e\t\t\t\t%8.2f' \
            '\n#\ttheta   [ ]  \t\t  = %5.8f\t\t\t%.3e\t\t\t\t%8.2f\n#\n#\tQdl/mgpt = %5.6f\n#\tL2 norm of res = %10.8f' % (
                float(self.finalParams[1]) * float(self.area.IE.get()),
                float(self.standardDeviation[1]) * float(self.area.IE.get()), self.percentSigma[1],
                float(self.finalParams[2]) * float(self.area.IE.get()),
                float(self.standardDeviation[2]) * float(self.area.IE.get()), self.percentSigma[2],
                float(self.finalParams[3]), float(self.standardDeviation[3]), self.percentSigma[3],
                float(self.finalParams[4]), float(self.standardDeviation[4]), self.percentSigma[4],
                float(self.finalParams[0]) * float(self.area.IE.get()),
                float(self.standardDeviation[0]) * float(self.area.IE.get()), self.percentSigma[0],
                float(self.finalParams[5]), float(self.standardDeviation[5]), self.percentSigma[5],
                float(self.finalParams[3]) / (float(self.area.IE.get()) * float(self.loading.IE.get())),
                float(self.L2NormOfRes)))

        dataOutFile.write('\n#\tAvg. |Z| residual % WRT to data |Z| = ' + str(self.resPercentData))

        dataOutFile.close()
        print("saved data in: " + self.currentDataDir.IE.get() + self.activeData.dataNameNoExt + '_fit.txt')

    # Because built in coth(x) cant deal with complex numbers because exp(x) cant deal with them, but pow(x,y) can.
    def JPcoth(self, x):
        return (pow(np.e, x) + pow(np.e, -x)) / (pow(np.e, x) - pow(np.e, -x))

    # Minimizing this function results in fitting the real and complex parts of the impedance at the same time.
    def funcCost(self, params):
        if self.model_selection.get() == self.eis_model[0]:
            return np.array(np.sqrt(pow((self.funcreal(params) - self.activeData.zPrime), 2) + pow(
                (self.funcImg(params) - self.activeData.ZdoublePrime), 2)))
        elif self.model_selection.get() == self.eis_model[1]:
            return np.array(np.sqrt(pow((self.funcreal_l(params) - self.activeData.zPrime), 2) + pow(
                (self.funcImg_l(params) - self.activeData.ZdoublePrime), 2)))
        elif self.model_selection.get() == self.eis_model[2]:
            return np.array(np.sqrt(pow((self.funcreal_s(params) - self.activeData.zPrime), 2) + pow(
                (self.funcImg_s(params) - self.activeData.ZdoublePrime), 2)))
        else:
            print("Error in Model Selection")

    '''
        def funcCost_l(self, params):
            return np.array(np.sqrt(pow((self.funcreal_l(params) - self.activeData.zPrime), 2) + pow(
                (self.funcImg_l(params) - self.activeData.ZdoublePrime), 2)))

        def funcCost_s(self, params):
            return np.array(np.sqrt(pow((self.funcreal_s(params) - self.activeData.zPrime), 2) + pow(
                (self.funcImg_s(params) - self.activeData.ZdoublePrime), 2)))
    '''

    # Define the functions of the model (equation 2 from "A Physics-Based Impedance Model of Proton Exchange Membrane Fuel
    # Cells Exhibiting Low-Frequency Inductive Loops")

    def funcAbs(self, param):
        if self.model_selection.get() == self.eis_model[0]:
            return abs(self.funcreal(param) + 1j * self.funcImg(param))
        elif self.model_selection.get() == self.eis_model[1]:
            return abs(self.funcreal_l(param) + 1j * self.funcImg_l(param))
        elif self.model_selection.get() == self.eis_model[2]:
            return abs(self.funcreal_s(param) + 1j * self.funcImg_s(param))

        '''def funcAbs_s(self, param):
            return abs(self.funcreal_s(param) + 1j * self.funcImg_s(param))
        '''

    def funcPhase(self, param):
        if self.model_selection.get() == self.eis_model[0]:
            return 180 / np.pi * np.arctan(self.funcImg(param) / self.funcreal(param))
        elif self.model_selection.get() == self.eis_model[1]:
            return 180 / np.pi * np.arctan(self.funcImg_l(param) / self.funcreal_l(param))
        elif self.model_selection.get() == self.eis_model[2]:
            return 180 / np.pi * np.arctan(self.funcImg_s(param) / self.funcreal_s(param))

    #Function from Setzler
    def funcreal(self, param):
        return np.real(param[0] * pow((1j * 2 * np.pi * self.activeData.frequency), param[5]) + param[1] + pow(
            (param[2] / (param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]))), 0.5) * self.JPcoth(
            pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])), 0.5)))

    def funcImg(self, param):
        return np.imag(param[0] * pow((1j * 2 * np.pi * self.activeData.frequency), param[5]) + param[1] + pow(
            (param[2] / (param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]))), 0.5) * self.JPcoth(
            pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])), 0.5)))

    # 1-D linear diffusion model
    def funcreal_l(self, param):
        return np.real(
            param[0] * pow((1j * 2 * np.pi * self.activeData.frequency), param[5]) + param[1] + param[2] * pow(
                (param[2] * (param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]))),
                -0.5) * self.JPcoth(
                pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])), 0.5)))

    def funcImg_l(self, param):
        return np.imag(
            param[0] * pow((1j * 2 * np.pi * self.activeData.frequency), param[5]) + param[1] + param[2] * pow(
                (param[2] * (param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]))),
                -0.5) * self.JPcoth(
                pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])), 0.5)))

    # 1-D spherical diffusion model
    def funcreal_s(self, param):
        return np.real(param[0] * pow((1j * 2 * np.pi * self.activeData.frequency), param[5]) + param[1] + param[2] /
                       (pow(param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]), 0.5) *
                        self.JPcoth(
                            pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])),
                                0.5)) - 1))

    def funcImg_s(self, param):
        return np.imag(param[0] * pow((1j * 2 * np.pi * self.activeData.frequency), param[5]) + param[1] + param[2] /
                       (pow(param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]), 0.5) *
                        self.JPcoth(
                            pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])),
                                0.5)) - 1))

        #   pow((-1 + (param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]), 0.5) *
        #   self.JPcoth( pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])), 0.5))),
        #   -1))

        # return np.imag(param[0] * pow((1j * 2 * np.pi * self.activeData.frequency), param[5]) + param[1] + param[2] *
        #    pow((-1 + ((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4]), 0.5)
        #    *self.JPcoth(pow((param[2] * param[3] * pow((1j * 2 * np.pi * self.activeData.frequency), param[4])), 0.5)))),
        #    -1))


class Param():

    def __init__(self):
        self.IE = Entry()
        self.OE = Entry()
        self.OESD = Entry()
        self.OESDP = Entry()
        self.AVGRESPER = Entry()


@dataclass
class Data:
    dataName: str = ''
    dataNameNoExt: str = ''

    zPrime: list = field(default_factory=list)
    ZdoublePrime: list = field(default_factory=list)
    zMod: list = field(default_factory=list)
    modZExperimentalComplex: list = field(default_factory=list)
    frequency: np.ndarray = field(default_factory=lambda: np.array([]))
    phase: list = field(default_factory=list)

    rawzPrime: list = field(default_factory=list)
    rawZdoublePrime: list = field(default_factory=list)
    rawzMod: list = field(default_factory=list)
    rawmodZExperimentalComplex: list = field(default_factory=list)
    rawFrequency: list = field(default_factory=list)
    rawPhase: list = field(default_factory=list)


def on_closing():
    if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
        app.KILLALL()
        root.destroy()
        os._exit(0)


root = Tk()
app = OSIF(root)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()