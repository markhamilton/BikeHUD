#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from PyQt4.Qt import *

class SensorData():
	def __init__(self, metric = False):
		self.metric = metric

	def isSpeedDangerous(self):
		return self.getSpeed() > (30, 48)[self.metric]

	def getSpeed(self):
		# TODO: Get data from sensors
		currentMph = 31.0456135
		currentSpeed = currentMph * (1, 1.609344)[self.metric]
		return min(currentSpeed, 99)

	def getSpeedString(self):
		return '{0:g}'.format(round(self.getSpeed()))

	def getBatteryPercent(self):
		return 32.4;


class SensorWidget(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.setMinimumSize(100, 100)

		self.numCoils 		= 9 # must be a multiple of 3 for 3-phase motor
		self.coils 			= []
		self.sensors 		= SensorData(False)

		self.background 	= QColor(0, 0, 0)
		self.brightMono		= QColor(255, 20, 20)
		self.darkMono 		= QColor(200, 10, 10)
		self.penBattOutline	= QPen(self.brightMono, 4)

		self.fontSpeed 		= QFont('Liberation Sans Narrow')
		self.fontSpeedUnit 	= QFont('Liberation Sans Narrow')
		self.fontSlowDown	= QFont('Liberation Sans Narrow')

		self.penBattOutline.setCapStyle(Qt.SquareCap)
		self.penBattOutline.setJoinStyle(Qt.MiterJoin)
		self.fontSpeed.setBold(True)

	def paintEvent(self, e):
		clientrect = self.getClientRect()

		dc = QPainter(self)
		dc.fillRect(clientrect, self.background)
		dc.setPen(self.brightMono)

		## draw odometer
		strSpeed 		= self.sensors.getSpeedString()
		strSpeedUnit 	= ("mph", "kph")[self.sensors.metric]

		dc.setFont(self.fontSpeed)
		fmSpeed 		= QFontMetrics(self.fontSpeed)
		fmSpeedUnit		= QFontMetrics(self.fontSpeedUnit)
		pxSpeedW 		= fmSpeed.width(strSpeed)
		pxSpeedH 		= fmSpeed.height()
		pxSpeedUnitW	= fmSpeedUnit.width(strSpeedUnit)
		pxSpeedUnitH	= fmSpeedUnit.height()
		rcSpeedUnit		= QRect(clientrect.center() + QPoint(pxSpeedW / 2, -pxSpeedH / 2 - fmSpeed.descent() + fmSpeedUnit.descent()), QSize(pxSpeedUnitW, pxSpeedH))

		dc.drawText(clientrect, Qt.AlignCenter, strSpeed)
		dc.setFont(self.fontSpeedUnit)
		dc.drawText(rcSpeedUnit, Qt.AlignBottom, strSpeedUnit)

		## draw battery meter
		sizeBattery		= QSize(clientrect.width() / 8, clientrect.height() / 32)
		rcBattery		= QRect(clientrect.center() - QPoint(sizeBattery.width() / 2, (pxSpeedH - sizeBattery.height()) / 2), sizeBattery)

		dc.setPen(self.penBattOutline)
		dc.drawRect(rcBattery)
		dc.fillRect(rcBattery, self.darkMono)

		## draw speed warning for speeds over 30mph / 48kph
		if self.sensors.isSpeedDangerous():
			strSlow		= "SLOW"
			strDown		= "DOWN"
			fmSlowDown	= QFontMetrics(self.fontSlowDown)
			pxSlowDownW	= max(fmSlowDown.boundingRect(strSlow).width(), fmSlowDown.boundingRect(strDown).width())
			pxSlowDownH = clientrect.height() / 5
			rcSlowDown	= QRect(clientrect.center() - QPoint(pxSlowDownW + pxSpeedW / 2 + clientrect.width() / 30, pxSlowDownH / 2), QSize(pxSlowDownW, pxSlowDownH))

			dc.fillRect(rcSlowDown, Qt.blue)
			dc.drawText(rcSlowDown, Qt.AlignHCenter | Qt.AlignTop, strSlow)
			dc.drawText(rcSlowDown, Qt.AlignHCenter | Qt.AlignBottom, strDown)

			# TODO: Draw X


	def getClientRect(self):
		dim = min(self.width(), self.height())
		return QRect((self.width() - dim) / 2, (self.height() - dim) / 2, dim, dim)

	def resizeEvent(self, e):
		dim = min(self.width(), self.height())
		self.fontSpeed.setPixelSize(dim / 3)
		self.fontSpeedUnit.setPixelSize(dim / 18)
		self.fontSlowDown.setPixelSize(dim / 24)


class MainWindow(QMainWindow):
	def __init__(self, *args):
		QMainWindow.__init__(self, *args)
		self.wnd = QWidget(self)
		self.sensors = SensorWidget()
		self.setCentralWidget(self.sensors)


class BikeHudApp(QApplication):
	def __init__(self, *args):
		QApplication.__init__(self, *args)
		
		pal = self.palette()
		pal.setColor(QPalette.Background, Qt.gray)
		self.setPalette(pal)

		self.wnd = MainWindow()
		self.connect(self, SIGNAL("lastWindowClosed()"), self.shutdown)
		self.wnd.setGeometry(QRect(100, 100, 600, 600))
		self.wnd.show()

	def shutdown(self):
		self.exit(0)


def main(args):
	global app
	app = BikeHudApp(args)
	app.exec_()


if __name__ == "__main__":
	main(sys.argv)