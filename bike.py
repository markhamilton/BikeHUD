#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from PyQt4.Qt import *
from random import random

class SensorData():
	def __init__(self, metric = False):
		self.numCoils 		= 9 		# must be a multiple of 3
		self.metric 		= metric
		self.coils 			= []
		self.battery 		= 32.4
		self.speed 			= 30.0456135

		for ii in range(0, self.numCoils):
			self.coils.append(MagneticCoil)

	def updateCoils(self):
		for coil in self.coils:
			coil.updateCoil()

	def isSpeedDangerous(self):
		# safe limit is 30mph / 48kph
		return self.getSpeed() > (30, 48)[self.metric]

	def getSpeed(self):
		currentSpeed = self.speed * (1, 1.609344)[self.metric]
		return min(currentSpeed, 99)

	def getSpeedString(self):
		return '{0:g}'.format(round(self.getSpeed()))

	def getBatteryPercent(self):
		return self.battery;

class MagneticCoil():
	def __init__(self, coilIndex):
		self.coilIndex 		= coilIndex
		self.heatHistory 	= []
		self.powerHistory 	= []

		for ii in range(0, 10):
			self.heatHistory.append(0)
			self.powerHistory.append(0)

	def updateCoil(self):
		# TODO: Get real sensor data
		self.heatHistory.append(random(0.0, 10.0))
		self.heatHistory.popleft()
		self.powerHistory.append(random(0.0, 10.0))
		self.powerHistory.popleft()

class SensorWidget(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.setMinimumSize(100, 100)

		self.sensors 		= SensorData(False)

		self.background 	= QColor(0, 0, 0)
		self.brightMono		= QColor(255, 20, 20)
		self.darkMono 		= QColor(200, 10, 10)
		self.penBattOutline	= QPen(self.brightMono, 2)
		self.coilColors 	= [QColor(204, 150, 54), QColor(75, 135, 101), QColor(146, 8, 85)] # other interesting colors: QColor(246, 7, 72)

		self.fontSpeed 		= QFont('Liberation Sans Narrow')
		self.fontSpeedUnit 	= QFont('Liberation Sans Narrow')
		self.fontSlowDown	= QFont('Liberation Sans Narrow')
		self.fontSlipTicks	= QFont('Liberation Sans Narrow')

		self.penBattOutline.setCapStyle(Qt.SquareCap)
		self.penBattOutline.setJoinStyle(Qt.MiterJoin)
		self.fontSpeed.setBold(True)

	def initCoils(self):
		for ii in range(0, self.numCoils):
			self.coils.append()

	def paintEvent(self, e):
		clientrect = self.getClientRect()
		dim = clientrect.height()
		pad = dim / 40

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
		rcBattery		= QRect(clientrect.center() - QPoint(sizeBattery.width() / 2, (pxSpeedH - sizeBattery.height()) / 2 + pad), sizeBattery)

		# TODO: Finish this, it looks awful as-is:
		# dc.drawRect(rcBattery)
		# dc.fillRect(rcBattery, self.darkMono)

		## draw speed warning for speeds over safe limit
		if self.sensors.isSpeedDangerous():
			strSlow		= "SLOW"
			strDown		= "DOWN"
			fmSlowDown	= QFontMetrics(self.fontSlowDown)
			pxSlowDownW	= max(fmSlowDown.width(strSlow), fmSlowDown.width(strDown))
			pxSlowDownH = pxSpeedH - fmSpeed.descent() * 4
			rcSlowDown	= QRect(clientrect.center() - QPoint(pxSlowDownW + pxSpeedW / 2, pxSlowDownH / 2), QSize(pxSlowDownW, pxSlowDownH))

			dc.setFont(self.fontSlowDown)
			dc.drawText(rcSlowDown, Qt.AlignHCenter | Qt.AlignTop, strSlow)
			dc.drawText(rcSlowDown, Qt.AlignHCenter | Qt.AlignBottom, strDown)
			# TODO: Draw X between SLOW and DOWN

		## generate coil drawing paths
		radSlipTickMin	= dim / 1.24
		radSlipTickMaj	= dim / 1.26
		radSlipOuter	= dim / 1.3
		radSlipInner	= dim / 1.7
		radMagOuter		= dim / 0.5
		radMagInner		= dim / 0.9
		rcSlipTickMaj 	= QRectF(clientrect.center().x() - radSlipTickMaj / 2, clientrect.center().y() - radSlipTickMaj / 2, radSlipTickMaj, radSlipTickMaj)
		rcSlipTickMin 	= QRectF(clientrect.center().x() - radSlipTickMin / 2, clientrect.center().y() - radSlipTickMin / 2, radSlipTickMin, radSlipTickMin)
		rcSlipOuter 	= QRectF(clientrect.center().x() - radSlipOuter / 2, clientrect.center().y() - radSlipOuter / 2, radSlipOuter, radSlipOuter)
		rcSlipInner 	= QRectF(clientrect.center().x() - radSlipInner / 2, clientrect.center().y() - radSlipInner / 2, radSlipInner, radSlipInner)
		rcMagOuter		= QRectF(clientrect.center().x() - radMagOuter / 2, clientrect.center().y() - radMagOuter / 2, radMagOuter, radMagOuter)
		rcMagInner		= QRectF(clientrect.center().x() - radMagInner / 2, clientrect.center().y() - radMagInner / 2, radMagInner, radMagInner)
		fmSlipTicks		= QFontMetrics(self.fontSlipTicks)
		degSpacer		= 0.5
		degCoilInterval	= (360 / self.sensors.numCoils)
		degCoilSpan		= degCoilInterval - (degSpacer * self.sensors.numCoils)

		## Draw coil slip and heat graph, and then magnetic field strength
		nCoil = 0
		for coil in self.sensors.coils:
			nPath 				= nCoil % 3
			pathSlip 			= QPainterPath()
			pathField 			= QPainterPath()
			degPathIncrement 	= degCoilSpan / 10 #len(coil.powerHistory)

			pathSlip.arcMoveTo(rcSlipOuter, nCoil * degCoilInterval)
			pathSlip.arcTo(rcSlipOuter, nCoil * degCoilInterval, -degCoilSpan)
			pathSlip.arcTo(rcSlipInner, nCoil * degCoilInterval - degCoilSpan, 0)
			pathSlip.arcTo(rcSlipInner, nCoil * degCoilInterval - degCoilSpan, degCoilSpan)
			pathSlip.closeSubpath()

			dc.setPen(self.coilColors[nPath])
			dc.setFont(self.fontSlipTicks)

			tickMajor = True
			for tick in range(0, 11):
				degTickAngle = (nCoil * degCoilInterval) - (tick * 0.1) * degCoilSpan

				# """not necessary for now and buggy (colors for text are phase shifted)"""
				# if tickMajor:
				# 	dc.save()
				# 	dc.translate(clientrect.center())
				# 	dc.rotate(degTickAngle)
				# 	dc.translate(QPoint(rcSlipTickMaj.height() / 2 + pad, -fmSlipTicks.height() / 2))
				# 	dc.drawText(0, 0, str(tick * 10))
				# 	dc.restore()

				pathSlip.arcMoveTo(rcSlipOuter, degTickAngle)
				pathSlip.arcTo((rcSlipTickMaj, rcSlipTickMin)[tickMajor], degTickAngle, 0)
				pathSlip.closeSubpath()
				tickMajor = not tickMajor

			dc.drawPath(pathSlip)

			# TODO: generate the graph for field power history
			# pathField.arcMoveTo(rcMagInner, nCoil * degCoilInterval)
			# for powerLevel in powerHistory:
			# 	radPower = radMagInner + (powerLevel / 10) * (radMagOuter - radMagInner)
			# 	pathField.arcTo()

			nCoil += 1
			

	def getClientRect(self):
		dim = min(self.width(), self.height())
		return QRect((self.width() - dim) / 2, (self.height() - dim) / 2, dim, dim)

	def resizeEvent(self, e):
		dim = min(self.width(), self.height())

		## resize fonts
		self.fontSpeed.setPixelSize(dim / 3)
		self.fontSpeedUnit.setPixelSize(dim / 18)
		self.fontSlowDown.setPixelSize(dim / 24)
		self.fontSlipTicks.setPixelSize(dim / 30)

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
		self.wnd.setGeometry(QRect(100, 100, 400, 400))
		self.wnd.show()
		# self.wnd.showFullScreen()

	def shutdown(self):
		self.exit(0)


def main(args):
	global app
	app = BikeHudApp(args)
	app.exec_()


if __name__ == "__main__":
	main(sys.argv)