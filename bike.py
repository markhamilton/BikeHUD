#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from PyQt4.Qt import *

class SensorData():
	def __init__(self, metric = False):
		self.metric = metric

	def getSpeed(self):
		# TODO: Get data from sensors
		currentMph = 31.0456135
		return currentMph * (1, 1.609344)[self.metric]

	def getSpeedString(self):
		return '{0:g}'.format(round(self.getSpeed()))


class SensorWidget(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.setMinimumSize(100, 100)

		self.numCoils 		= 9 # must be a multiple of 3 for 3-phase motor
		self.coils 			= []
		self.sensors 		= SensorData(False)

		self.brightRed 		= QColor(255, 20, 20)
		self.darkRed 		= QColor(200, 10, 10)

		self.fontSpeed 		= QFont('Liberation Sans Narrow')
		self.fontSpeedUnit 	= QFont('Liberation Sans Narrow')

		self.fontSpeed.setBold(True)

	def paintEvent(self, e):
		clientrect = self.getClientRect()

		dc = QPainter(self)
		dc.fillRect(clientrect, Qt.black)
		dc.setPen(self.brightRed)
		self.drawOdometer(dc, clientrect)

	def drawOdometer(self, dc, clientrect):
		strSpeed 		= self.sensors.getSpeedString()
		strSpeedUnit 	= ("mph", "kph")[self.sensors.metric]

		dc.setFont(self.fontSpeed)
		fmSpeed 		= QFontMetrics(self.fontSpeed)
		fmSpeedUnit		= QFontMetrics(self.fontSpeedUnit)
		pxSpeedW 		= fmSpeed.width(strSpeed)
		pxSpeedH 		= fmSpeed.height()
		pxSpeedUnitW	= fmSpeedUnit.width(strSpeedUnit)
		pxSpeedUnitH	= fmSpeedUnit.height()
		center 			= clientrect.center()

		dc.drawText(clientrect, Qt.AlignCenter, strSpeed)
		dc.setFont(self.fontSpeedUnit)
		dc.drawText(center + QPoint(pxSpeedW / 2, pxSpeedH / 2 - pxSpeedUnitH), strSpeedUnit)

	def getClientRect(self):
		dim = min(self.width(), self.height())
		return QRect((self.width() - dim) / 2, (self.height() - dim) / 2, dim, dim)

	def resizeEvent(self, e):
		dim = min(self.width(), self.height())
		self.fontSpeed.setPixelSize(dim / 3)
		self.fontSpeedUnit.setPixelSize(dim / 24)

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