#!/usr/bin/env python
#-*- coding: utf-8 -*-

## TODO (Housekeeping) ##
# Break out colors, customizable settings and place them into ConfigSettings
# Load ConfigSettings from file
# When rounding the HUD will read -0 sometimes

import sys
from PyQt4.Qt import *
from random import random
from datetime import datetime

class ConfigSettings:
	## i18n
	metric 					= False

	## motor configuration
	## this just calibrates the HUD; no change to output driver is made
	numCoils				= 9 # must be a multiple of 3
	motorCurrent			= 9 # in amps

	## disable antialiasing for smoother performance
	lineAntialiasing 		= True
	textAntialiasing 		= True

	## target device resolution will change depending on PC board
	## this can be set dynamically instead if needed but I kept it fixed for ease of testing
	targetResolution = QRect(100, 100, 800, 480)


class SensorData():
	def __init__(self):
		self.coils 			= []
		self.speed 			= 30

		for ii in range(0, ConfigSettings.numCoils):
			self.coils.append(MagneticCoil(ii))

		self.updateSensorsHighPriority()
		self.updateSensorsMediumPriority()
		self.updateSensorsLowPriority()

	def isSpeedDangerous(self):
		# safe limit is 30mph / 48kph
		return self.getSpeed() > (30, 48)[ConfigSettings.metric]

	def getSpeed(self):
		currentSpeed = self.speed * (1, 1.609344)[ConfigSettings.metric]
		return min(currentSpeed, 99)

	def getSpeedString(self):
		return str(round(self.getSpeed()))[:-2]

	def getBatteryPercent(self):
		return self.battery

	def getTime(self):
		return self.time

	def updateSensorsHighPriority(self):
		self.time 			= str(datetime.now().time())[:-2]

	def updateSensorsMediumPriority(self):
		self.speed 			= self.speed + random() * 2.0 - 1.0

		for coil in self.coils:
			coil.updateCoil()

	def updateSensorsLowPriority(self):
		self.date 			= datetime.now().date()

	def updateSensorsVeryLowPriority(self):
		self.battery 		= random() * 100.0

	def getDate(self):
		return self.date

class MagneticCoil():
	def __init__(self, coilIndex):
		self.coilIndex 		= coilIndex
		self.heatHistory 	= []
		self.powerHistory 	= []

		for ii in range(0, 11):
			self.heatHistory.append(0)
			self.powerHistory.append(0)

		# TODO: Remove this fake data
		for ii in self.heatHistory:
			self.updateCoil()

	def updateCoil(self):
		# TODO: Get real sensor data
		self.heatHistory.append(random() * 10.0)
		self.heatHistory.pop(0)
		self.powerHistory.append(random() * 10.0)
		self.powerHistory.pop(0)

class SwitcherWidget(QWidget):
	def __init__(self, parent=0):
		QWidget.__init__(self, parent)

		self.btnGroup 	= QButtonGroup(self)
		self.btnWiring 	= QPushButton(self)


class WiringWidget(QWidget):
	def __init__(self, parent=0):
		QWidget.__init__(self, parent)
		self.background 	= QColor(0, 0, 0)
		self.fontLabel 		= QFont('Liberation Mono')
		self.fontValues		= QFont('Liberation Sans Narrow')

	def paintEvent(self, e):
		clientrect 			= self.getClientRect()
		dim 				= clientrect.height()
		pad 				= dim / 40
		dc 					= QPainter(self)

		dc.fillRect(clientrect, self.background)

		## create timing grid
		fmTickValues		= QFontMetrics(self.fontValues)
		pxTickMaxStrW		= fmTickValues.width(str(float(ConfigSettings.motorCurrent)))
		pxTickMaxStrH		= fmTickValues.height()
		rcTimingGrid 		= QRect(clientrect.width() / 10, clientrect.height() / 2, clientrect.width() * 0.8, clientrect.height() / 2)
		rcTimingRange		= QRect(rcTimingGrid.x() + pad + pxTickMaxStrW, rcTimingGrid.y(), rcTimingGrid.width() - pad - pxTickMaxStrW, rcTimingGrid.height() - pad - pxTickMaxStrH)
		pathTimingRange		= QPainterPath()

		dc.fillRect(rcTimingGrid, Qt.gray)

		pathTimingRange.moveTo(rcTimingRange.x(), rcTimingRange.y())
		pathTimingRange.lineTo(rcTimingRange.x(), rcTimingRange.bottomLeft().y())
		pathTimingRange.lineTo(rcTimingRange.bottomRight().x(), rcTimingRange.bottomRight().y())

		gridSteps 			= 11
		for yy in range(0, gridSteps):
			pxTickY 		= rcTimingRange.y() + (gridSteps - yy) * ((rcTimingRange.height() - pad)) / 11
			strAmps			= str(round((float(yy) / float(gridSteps)) * ConfigSettings.motorCurrent, 1)) + " A"

			fmTickValues.width(strAmps)
			pathTimingRange.moveTo(rcTimingGrid.x() + pxTickMaxStrW, pxTickY)
			pathTimingRange.lineTo(rcTimingRange.x(), pxTickY)

		dc.setPen(Qt.blue)
		dc.drawPath(pathTimingRange)

	def getClientRect(self):
		dim = min(self.width(), self.height())
		return QRect((self.width() - dim) / 2, (self.height() - dim) / 2, dim, dim)


class SensorWidget(QWidget):
	def __init__(self, parent=0):
		QWidget.__init__(self, parent)

		self.sensors 			= SensorData()

		## tweak colors to your preference
		self.background 		= QColor(0, 0, 0)
		self.brightMono			= QColor(255, 20, 20)
		self.darkMono 			= QColor(102, 8, 8)
		self.magPower 	 		= QColor(246, 7, 72)
		self.magPowerDark 		= QColor(51, 1, 15)
		self.penBattOutline		= QPen(self.brightMono, 2)

		## coil colors are: [yellow, green, magenta]
		self.coilColorsBright	= [QColor(254, 188, 68), QColor(103, 186, 139), QColor(196, 11, 114)]
		self.coilColors 		= [QColor(153, 113, 41), QColor(47, 84, 63), QColor(94, 5, 55)]
		self.coilColorsDark		= [QColor(77, 56, 20), QColor(29, 51, 38), QColor(51, 3, 30)]

		## tweak fonts to your preference (you need a narrow font!)
		self.fontSpeed 			= QFont('Liberation Sans Narrow')
		self.fontSpeedUnit 		= QFont('Liberation Sans Narrow')
		self.fontSlowDown		= QFont('Liberation Sans Narrow')
		self.fontSlipTicks		= QFont('Liberation Sans Narrow')
		self.fontTime 			= QFont('Liberation Sans Narrow')

		self.fontSpeed.setBold(True)

		self.penBattOutline.setCapStyle(Qt.SquareCap)
		self.penBattOutline.setJoinStyle(Qt.MiterJoin)

		## set timers to update sensors
		self.timerHigh 			= QTimer()
		self.timerMedium		= QTimer()
		self.timerLow 			= QTimer()
		self.timerVeryLow		= QTimer()

		self.timerHigh.timeout.connect(self.updateHighPriority)
		self.timerMedium.timeout.connect(self.updateMediumPriorty)
		self.timerLow.timeout.connect(self.updateLowPriority)
		self.timerVeryLow.timeout.connect(self.updateVeryLowPriority)
		
		self.timerHigh.start(10)
		self.timerMedium.start(600)
		self.timerLow.start(2000)
		self.timerVeryLow.start(2 * 60 * 2000) # 2 minutes

	def updateHighPriority(self):
		self.sensors.updateSensorsHighPriority()
		self.repaint()

	def updateMediumPriorty(self):
		self.sensors.updateSensorsMediumPriority()

	def updateLowPriority(self):
		self.sensors.updateSensorsLowPriority()

	def updateVeryLowPriority(self):
		self.sensors.updateSensorsVeryLowPriority()

	def paintEvent(self, e):
		clientrect 		= self.getClientRect()
		dim 			= clientrect.height()
		pad 			= dim / 40
		dc 				= QPainter(self)

		dc.fillRect(clientrect, self.background)
		dc.setRenderHint(QPainter.Antialiasing, ConfigSettings.lineAntialiasing)
		dc.setRenderHint(QPainter.TextAntialiasing, ConfigSettings.textAntialiasing)
		dc.setPen(self.brightMono)

		## draw odometer
		strSpeed 		= self.sensors.getSpeedString()
		strSpeedUnit 	= ("mph", "kph")[ConfigSettings.metric]

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

		## draw current time
		fmTime			= QFontMetrics(self.fontTime)
		rcTimeText 		= QRect(clientrect.left(), clientrect.center().y() + (pxSpeedH / 2) - fmSpeed.descent() + pad, clientrect.width(), fmTime.height())
		rcDateText 		= QRect(clientrect.left(), rcTimeText.bottomRight().y(), clientrect.width(), fmTime.height())

		dc.setFont(self.fontTime)
		dc.setPen(self.darkMono)
		dc.drawText(rcTimeText, Qt.AlignCenter, str(self.sensors.getTime()))
		dc.drawText(rcDateText, Qt.AlignCenter, str(self.sensors.getDate()))

		## draw speed warning for speeds over safe limit
		if self.sensors.isSpeedDangerous():
			strSlow		= "SLOW"
			strDown		= "DOWN"
			fmSlowDown	= QFontMetrics(self.fontSlowDown)
			pxSlowDownW	= max(fmSlowDown.width(strSlow), fmSlowDown.width(strDown))
			pxSlowDownH = pxSpeedH - fmSpeed.descent() * 4
			rcSlowDown	= QRect(clientrect.center() - QPoint(pxSlowDownW + pxSpeedW / 2, pxSlowDownH / 2), QSize(pxSlowDownW, pxSlowDownH))

			dc.setFont(self.fontSlowDown)
			dc.setPen(self.brightMono)
			dc.drawText(rcSlowDown, Qt.AlignHCenter | Qt.AlignTop, strSlow)
			dc.drawText(rcSlowDown, Qt.AlignHCenter | Qt.AlignBottom, strDown)
			# Suggestion: Draw X between SLOW and DOWN?

		## generate coil sensor drawing paths
		radSlipTickMin	= dim / 1.24
		radSlipTickMaj	= dim / 1.26
		radSlipOuter	= dim / 1.3
		radSlipInner	= dim / 1.7
		radMagOuter		= dim / 1.01
		radMagInner		= dim / 1.2
		rcSlipTickMaj 	= QRectF(clientrect.center().x() - radSlipTickMaj / 2, clientrect.center().y() - radSlipTickMaj / 2, radSlipTickMaj, radSlipTickMaj)
		rcSlipTickMin 	= QRectF(clientrect.center().x() - radSlipTickMin / 2, clientrect.center().y() - radSlipTickMin / 2, radSlipTickMin, radSlipTickMin)
		rcSlipOuter 	= QRectF(clientrect.center().x() - radSlipOuter / 2, clientrect.center().y() - radSlipOuter / 2, radSlipOuter, radSlipOuter)
		rcSlipInner 	= QRectF(clientrect.center().x() - radSlipInner / 2, clientrect.center().y() - radSlipInner / 2, radSlipInner, radSlipInner)
		rcMagOuter		= QRectF(clientrect.center().x() - radMagOuter / 2, clientrect.center().y() - radMagOuter / 2, radMagOuter, radMagOuter)
		rcMagInner		= QRectF(clientrect.center().x() - radMagInner / 2, clientrect.center().y() - radMagInner / 2, radMagInner, radMagInner)
		fmSlipTicks		= QFontMetrics(self.fontSlipTicks)
		degSpacer		= (5.5 / ConfigSettings.numCoils, 0.0)[ConfigSettings.numCoils >= 60]
		degCoilInterval	= (360 / ConfigSettings.numCoils)
		degCoilSpan		= degCoilInterval - (degSpacer * ConfigSettings.numCoils)

		## Draw coil slip, and then magnetic field strength
		nCoil = 0
		for coil in self.sensors.coils:
			nPath 				= nCoil % 3
			pathSlip 			= QPainterPath()
			pathSlipGrid		= QPainterPath()
			pathField 			= QPainterPath()
			degPathIncrement 	= degCoilSpan / len(coil.powerHistory)

			pathSlip.arcMoveTo(rcSlipOuter, nCoil * degCoilInterval)
			pathSlip.arcTo(rcSlipOuter, nCoil * degCoilInterval, -degCoilSpan)
			pathSlip.arcTo(rcSlipInner, nCoil * degCoilInterval - degCoilSpan, 0)
			pathSlip.arcTo(rcSlipInner, nCoil * degCoilInterval - degCoilSpan, degCoilSpan)
			pathSlip.closeSubpath()

			## disabled: change the brush and font for tick values
			# dc.setPen(self.coilColors[nPath])
			# dc.setFont(self.fontSlipTicks)

			tickMajor = True
			for tick in range(0, 11):
				degTickAngle = (nCoil * degCoilInterval) - (tick * 0.1) * degCoilSpan

				## generate graph grid
				if tickMajor:
					pathSlipGrid.arcMoveTo(rcSlipInner, degTickAngle)
					pathSlipGrid.arcTo(rcSlipOuter, degTickAngle, 0)

					## disabled: draw tick values
					## not necessary for now. also buggy! (colors for text are phase shifted!)
					# dc.save()
					# dc.translate(clientrect.center())
					# dc.rotate(degTickAngle)
					# dc.translate(QPoint(rcSlipTickMaj.height() / 2 + pad, -fmSlipTicks.height() / 2))
					# dc.drawText(0, 0, str(tick * 10))
					# dc.restore()

				## generate graph tick marks
				pathSlip.arcMoveTo(rcSlipOuter, degTickAngle)
				pathSlip.arcTo((rcSlipTickMaj, rcSlipTickMin)[tickMajor], degTickAngle, 0)
				pathSlip.closeSubpath()
				tickMajor = not tickMajor

			dc.setPen(QPen(self.coilColorsDark[nPath], 1, Qt.DotLine))
			dc.drawPath(pathSlipGrid)
			dc.setPen(self.coilColorsBright[nPath])
			dc.drawPath(pathSlip)

			## generate the graph for field power history
			pathField.arcMoveTo(rcMagInner, nCoil * degCoilInterval)
			tickIndex = 0
			for powerLevel in coil.powerHistory:
				degTickAngle 	= (nCoil * degCoilInterval) - (tickIndex * 0.1) * degCoilSpan
				radPower 		= (powerLevel / 10) * (radMagOuter - radMagInner) + radMagInner
				rcPower 		= QRectF(clientrect.center().x() - radPower / 2, clientrect.center().y() - radPower / 2, radPower, radPower)
				pathField.arcTo(rcPower, degTickAngle, 0)
				tickIndex += 1

			pathField.arcTo(rcMagInner, nCoil * degCoilInterval - degCoilSpan, 0)
			pathField.arcTo(rcMagInner, nCoil * degCoilInterval - degCoilSpan, degCoilSpan)

			dc.setPen(self.magPower)
			dc.fillPath(pathField, self.magPowerDark)
			dc.drawPath(pathField)

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
		self.fontTime.setPixelSize(dim / 20)


class MainWindow(QMainWindow):
	def __init__(self, *args):
		QMainWindow.__init__(self, *args)
		self.wnd 		= QWidget(self)
		self.sensors 	= SensorWidget(self)
		self.wiring 	= WiringWidget(self)

		self.sensors.setGeometry(QRect(0, 0, ConfigSettings.targetResolution.width() / 2, 480))
		self.wiring.setGeometry(QRect(ConfigSettings.targetResolution.width() / 2, 0, ConfigSettings.targetResolution.width() / 2, 480))

		# self.setCentralWidget(self.sensors)


class BikeHudApp(QApplication):
	def __init__(self, *args):
		QApplication.__init__(self, *args)
		
		pal = self.palette()
		pal.setColor(QPalette.Background, Qt.gray)
		self.setPalette(pal)

		self.wnd = MainWindow()
		self.connect(self, SIGNAL("lastWindowClosed()"), self.shutdown)
		self.wnd.setGeometry(ConfigSettings.targetResolution)
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
