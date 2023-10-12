# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 00:34:05 2023

@author: margh
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QSlider, QPushButton, QLCDNumber
from PyQt5.QtCore import QSize
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


import numpy as np
import sys
#import matplotlib.pyplot as plt

qtCreatorFile = "C:/Users/margh/Downloads/gvs code2.ui"

Ui_MainWindow, QtBaseClass = loadUiType(qtCreatorFile)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        super().__init__()

        self.setupUi(self)
        self.setWindowTitle('gvscode')


        grafico = FigureCanvas(Figure(figsize=(8, 6), constrained_layout=True, edgecolor='black', frameon=True))
        self.Plotting_box.addWidget(grafico)

        self.grafico, self.grafico2 = grafico.figure.subplots( 2, 1, sharex=True)
        self.grafico.set_ylabel('E.coli cells concentrations (cells/ml)', size=7)
        self.grafico.set_title("E.coli growth in 24 hours", size=8, color="black")
        self.grafico2.set_ylabel("Gvs concentrations (gvs/ml)" , size=7)
        self.grafico2.set_xlabel("Time(hours)",size=7)
#
        t = np.arange(25) #hours
        cellsconc = np.zeros(25) #cells concentration
        self.grafico.plot(t, cellsconc, color="white")
        gvsconc = np.zeros(25)
        self.grafico2.plot(t, gvsconc, color="white")

        self.pushButton_7.clicked.connect(self.graphs) #button to plot the graphs
        self.pushButton_10.clicked.connect(self.detectithresold) #button to estimate when detection thresold reached
        
        self.T.setText("37") #at 37° it is optimal condition for E.coli growth
        self.ph.setText("6") #the ph in the colon is around 6
        self.watactivity.setText("0.997") 
        self.ox.setText("7") #the oxygen level of colon is between 6% and 10%
        self.growthrate.setText("1.8") #growth rate from Shapiro 2018 paper
        self.initialconc.setText("1000000") #the initial concentration of E.coli cells is chosen 10^6 cells/ml from paper Hurts 2023
        
        self.pr.setText("100") #the production rate of gvs for E.coli cell, the value is taken from Shapiro 2018
        self.nutrients.setText("0.8")#for further implementations, a formula for the effect of the parameter for nutriwnt availabilty on the growth rate need to be implemented in the formula which estimates the growth rate
        self.bfactor.setText("2.4") # buoyancy factor from Shapiro 2018
        self.dt.setText("50000000") #the detection thresold,thresold concentration of E.coli cells necessary to detect a signal from the gvs produced, taken from Shapiro 2018
        
        self.checkBox.stateChanged.connect(self.growrate) #checkbox to set the automatically the growth rate
        
    def graphs(self):
            initialconc = float(self.initialconc.toPlainText())
            growthrate1 = float(self.growthrate.toPlainText())
            
            productionrate = float(self.pr.toPlainText())# gas vescicles produced by each e. coli eveery hour, taken Shapiro 2018
            
            buoyancyfactor = float(self.bfactor.toPlainText())
            T= float(self.T.toPlainText())
            aw= float(self.watactivity.toPlainText())
            ph= float(self.ph.toPlainText())
            Ox=float(self.ox.toPlainText())
            if self.checkBox.isChecked():
                growthrate=growthrate1 
            else:
                if T>42.00 or T<4.14 or aw<0.9508 or ph<3.909 or ph>8.860:
                   growthrate=0 #the line is to account for the fact that if the parameters are set above or below some maximum or minimum values the E.coli do not grow
                if Ox<3.5: #the model assumes the when the oxuygen level is between 3.5$ and 20% it does not considerably affect the growth rate, when the oxygen level is below 3.5% the growth rate considerably decreases 
                   growthrate=0.255
                else: #formula that estimates the growth rate from the temperature, ph
                   growthrate=0.2345*(T-4.14)*(1-np.exp(T-42))*(aw-0.9508)**(1/2)*(1-10**(3.909-ph))**(1/2)*(1-10**(ph-8.860))**(1/2)
                
            t = np.arange(25)
            cellconc = np.zeros(25)
            gvconc = np.zeros(25)
            cellconc[0] = initialconc
            gvconc[0] = 0
            
            #to account for the steady phase of the E.coli growth and set a maximum concentration which the E.coli can reach before the steady phase
            if self.checkBox.isChecked():
                growthrateT=1.8
            else:
                growthrateT=0.2345*(37-4.14)*(1-np.exp(37-42))*(0.997-0.9508)**(1/2)*(1-10**(3.909-6))**(1/2)*(1-10**(6-8.860))**(1/2)
            cellconcT=np.zeros(25)
            cellconcT[0]=10**6 #from Hurt's paper
            for i in range(len(t)-1):
                if i < 8:
                    cellconcT[i+1] = cellconcT[i]*np.exp(growthrateT)
                else:
                    cellconcT[i+1] = cellconcT[i]
            print(cellconcT)
            
            #to approximate the growth of the E.coli cells (a lag phase, followed by an exponential growth and a steady phase)
            for i in range(len(t)-1):
                if cellconc[i]<cellconcT[8]:
                    cellconc[i+1] = cellconc[i]*np.exp(growthrate)
                    if cellconc[i+1]>cellconcT[8]:
                        cellconc[i+1]=cellconcT[8]
                if cellconc[i]>cellconcT[8]:
                    cellconc[i+1] = cellconc[i]
                if cellconc[i]==cellconcT[8]:
                     cellconc[i+1] = cellconc[i]
                    
                #to model the gvs production 
                gvconc[i+1] = (gvconc[i]+productionrate*cellconc[i+1])*buoyancyfactor
                
                
                if T>=42.00 or T<=4.14 or aw<=0.9508 or ph<=3.909 or ph>=8.860:  #gvs are not produced above and below those values sinceE.coli do not grow
                    gvconc[i+1]=gvconc[0]
            
            
            
           
            self.grafico.clear()
            self.grafico.plot(t, cellconc)
            self.grafico.set_ylabel("E.coli concentrations (cells/ml)", size=7)
            self.grafico.set_title("E.coli growth in 24 hours", size=8, color="black")
            self.grafico.figure.canvas.draw()
            self.grafico2.clear()
            self.grafico2.plot(t, gvconc)
            self.grafico2.set_xlabel('Time (hours)', size=7)
            self.grafico2.set_ylabel("GVs concentrations", size=7)
            self.grafico2.figure.canvas.draw()
            
            global thours
            thours=t
            global cellsconc
            cellsconc=cellconc
            global gvsconc
            gvsconc=gvconc

    
    def growrate(self): #if the user thicks the checkbox the growth rate can be set automatically
        if self.checkBox.isChecked():
            initialconc = float(self.initialconc.toPlainText())
            growthrate = float(self.growthrate.toPlainText()) #growthrate=1.8 from Hurt 2023
            productionrate = float(self.pr.toPlainText())# gas vescicles produced by each E.coli eveery hour
            
            buoyancyfactor = float(self.bfactor.toPlainText())
            
            t = np.arange(25)
            cellconc = np.zeros(25)
            gvconc = np.zeros(25)
            cellconc[0] = initialconc
            gvconc[0] = 0
            
            #tpo account for the steady phase of E.coli growth and set a maximum concentration that the E.coli reach before the steady phase
            growthrateT=1.8
            cellconcT=np.zeros(25)
            cellconcT[0]=10**6
            for i in range(len(t)-1):
                if i < 7:
                    cellconcT[i+1] = cellconcT[i]*np.exp(growthrateT)
                else:
                    cellconcT[i+1] = cellconcT[i]
            print(cellconcT)
            
            #to model the E.coli growth
            for i in range(len(t)-1):
                if cellconc[i]<cellconcT[7]:
                    cellconc[i+1] = cellconc[i]*np.exp(growthrate)
                    if cellconc[i+1]>cellconcT[7]:
                        cellconc[i+1]=cellconcT[7]
                if cellconc[i]>cellconcT[7]:
                    cellconc[i+1] = cellconc[i]
                if cellconc[i]==cellconcT[7]:
                     cellconc[i+1] = cellconc[i]

                #to model the gvs production
                gvconc[i+1] = (gvconc[i]+productionrate * cellconc[i+1])*buoyancyfactor
           
            
            self.grafico.clear()
            self.grafico.plot(t, cellconc)
            self.grafico.set_ylabel("E.coli concentrations (cells/ml)", size=7)
            self.grafico.set_title("E.coli growth in 24 hours", size=8, color="black")
            self.grafico.figure.canvas.draw()
            self.grafico2.clear()
            self.grafico2.plot(t, gvconc)
            self.grafico2.set_xlabel('Time (hours)', size=7)
            self.grafico2.set_ylabel("GVs concentrations", size=7)
            self.grafico2.figure.canvas.draw()
            
            global thours
            thours=t
            global cellsconc
            cellsconc=cellconc
            global gvsconc
            gvsconc=gvconc
            
            
    def detectithresold(self):  #to estimate the thresold E.coli concentration above which a signal from the gvs produced coulod be detected
         detectionThresold=float(self.dt.toPlainText())
         for i in range(len(thours)):
          if cellsconc[i] >= detectionThresold and cellsconc[i-1] < detectionThresold:
            print(thours[i])
            thoursr=str(thours[i])
            tvolume=100/cellsconc[i]
            tvolume=str(tvolume)
            self.lineEdit_7.setPlaceholderText(tvolume)
            self.lineEdit_10.setPlaceholderText(thoursr)
            
            
if __name__ == "__main__":
                app = QtWidgets.QApplication(sys.argv)
                window = MyApp()
                window.show()
                sys.exit(app.exec_())