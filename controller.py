from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import cv2
import os

import SFR
from UI import Ui_MainWindow


class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):  # init
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.path = f'{os.getcwd()}\img'
        self.ui.lineEditFileName.setText(self.path)
        self.UI_Connect()
        self.img = 0
        self.roi = 0
        self.FFTArr = np.zeros(10)
        self.Freq = self.ui.horizontalSliderFrequencyValue.value() / 10
        self.ui.labelFrequencyValue.setText(f'Frequency: {self.Freq}')

    def UI_Connect(self):  # 事件連結
        self.ui.pushButtonChoiceFile.clicked.connect(self.OpenFile)
        self.ui.pushButtonCalculate.clicked.connect(self.Calculate)
        self.ui.pushButtonShowFourierFunc.clicked.connect(self.ShowFourierFunc)
        self.ui.horizontalSliderFrequencyValue.valueChanged.connect(self.getslidervalue)
        self.ui.lineEditX.textEdited.connect(self.ReflashImage)
        self.ui.lineEditY.textEdited.connect(self.ReflashImage)
        self.ui.lineEditW.textEdited.connect(self.ReflashImage)
        self.ui.lineEditH.textEdited.connect(self.ReflashImage)

    def OpenFile(self):  # 選取文件
        self.path, filetype = QFileDialog.getOpenFileName(self, 'Open image', self.path, 'Images (*.png *.bmp *.jpg)')  # 開啟視窗名稱, 開啟資料夾, 種類Filter
        self.ui.lineEditFileName.setText(self.path)
        self.img = cv2.imread(self.path)  # 只讀取一次
        self.ReflashImage()  # 預設Show 出圖跟Roi

    def ReflashImage(self):  # Reflash
        if self.RefreshROIData():
            self.ShowImageRefrash()
            self.ShowROIRefrash()
        else:
            pass

    def ShowImageRefrash(self):
        if type(self.img) == np.ndarray:  # 確認影像有無
            img_show = self.img.copy()  # 要拿來畫圖的影像 copy 一份
            cv2.rectangle(img_show, (self.roi_x, self.roi_y), (self.roi_x + self.roi_w, self.roi_y + self.roi_h), (0, 0, 255), 3)
            cv2.putText(img_show, 'ROI', (self.roi_x, self.roi_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 3, cv2.LINE_AA)

            height, width, channel = img_show.shape
            bytesPerline = channel * width
            qimg = QImage(img_show, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()

            self.ui.labelImage.setPixmap(QPixmap.fromImage(qimg).scaledToWidth(self.ui.labelImage.width()))
            self.ui.labelImage.adjustSize()
            self.MsgRefresh('OK !!')

        else:
            self.MsgRefresh('Image is Empty !!')

    def ShowROIRefrash(self):
        if type(self.img) == np.ndarray:  # 確認影像有無
            self.roi = self.img[self.roi_y:self.roi_y + self.roi_h, self.roi_x:self.roi_x + self.roi_w].copy()
            height, width, channel = self.roi.shape
            bytesPerline = channel * width
            qroi = QImage(self.roi, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
            self.ui.labelROI.setPixmap(QPixmap.fromImage(qroi).scaledToWidth(self.ui.labelROI.width()))
            self.ui.labelROI.adjustSize()

    def getslidervalue(self):  # 0 ~ 1 (step: 0.1)
        self.Freq = self.ui.horizontalSliderFrequencyValue.value() / 10
        self.ui.labelFrequencyValue.setText(f'Frequency: {self.Freq}')
        self.SFRRefresh()

    def Calculate(self):
        if type(self.roi) == np.ndarray:  # 確認影像有無
            self.ReflashImage()
            roi_bw = cv2.cvtColor(self.roi, cv2.COLOR_BGR2GRAY)
            self.FFTArr = SFR.GetFFTArr(roi_bw)
            self.SFRRefresh()

            return True

        else:
            self.MsgRefresh('ROI is Empty !!')

            return False

    def ShowFourierFunc(self):
        if self.Calculate():
            SFR.ShowFFTImg(self.FFTArr)

    def SFRRefresh(self):
        self.SFRValue = SFR.GetArrFreqVal(self.FFTArr, self.Freq)
        self.ui.labelSFRValue.setText(f'SFR({self.Freq}): {self.SFRValue:.2f}')

    def MsgRefresh(self, Msg: str):
        self.ui.labelMsg.setText(Msg)
        print(Msg)

    def RefreshROIData(self):
        try:
            self.roi_x = int(self.ui.lineEditX.text())
            self.roi_y = int(self.ui.lineEditY.text())
            self.roi_w = int(self.ui.lineEditW.text())
            self.roi_h = int(self.ui.lineEditH.text())

            return True
        except:
            self.MsgRefresh('請設定整數')

            return False
