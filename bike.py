#!/usr/bin/env python
#-*- coding: utf-8 -*-

## TODO (Housekeeping) ##
# Break out colors and place them into ConfigSettings
# Load ConfigSettings from file
# Split this into multiple files

import sys
import math
from PyQt4.Qt import *
from random import random
from datetime import datetime

## Soon I will be moving these to a configuration file, but these will remain the defaults
class ConfigSettings:
	## i18n
	metric 					= False

	## motor configuration
	## this just calibrates the HUD; no change to output driver is made
	motorCoils				= 18  		# must be a multiple of 3
	motorCurrent			= 9 		# in amps
	motorVoltage			= 300 		# in volts
	loadRadius				= 22		# bike wheel radius, in inches/CM (depends on metric flag above)

	# misc settings
	showRPM					= True		# toggle this flag to show RPM vs speed (tap the sensor widget to toggle)

	## disable antialiasing for smoother performance possibly
	lineAntialiasing 		= True
	textAntialiasing 		= True

	## target device resolution will change depending on PC board
	## this can be set dynamically instead if needed but I kept it fixed for ease of testing
	targetResolution 		= QRect(100, 100, 800, 480)

	## coil colors are: [yellow, green, magenta]
	coilColorsBright		= [QColor(254, 188, 68), QColor(103, 186, 139), QColor(196, 11, 114)]
	coilColors 				= [QColor(153, 113, 41), QColor(47, 84, 63), QColor(94, 5, 55)]
	coilColorsDark			= [QColor(77, 56, 20), QColor(29, 51, 38), QColor(51, 3, 30)]

	## layout colors
	background 				= QColor(0, 0, 0)
	brightMono				= QColor(255, 20, 20)
	darkMono 				= QColor(102, 8, 8)
	magPower 	 			= QColor(246, 7, 72)
	magPowerDark 			= QColor(51, 1, 15)

class SensorData():
	def __init__(self):
		self.coils 			= []
		self.rpm			= 2500

		for ii in range(0, ConfigSettings.motorCoils):
			self.coils.append(MagneticCoil(ii))

		self.updateSensorsHighPriority()
		self.updateSensorsMediumPriority()
		self.updateSensorsLowPriority()

	def isSpeedDangerous(self):
		# safe limit is 30mph / 48kph
		return self.getSpeed() > (30, 48)[ConfigSettings.metric]

	def getRPM(self):
		return self.rpm

	def getRPMString(self):
		strRPM = str(round(self.getRPM()))[:-2]
		if strRPM == "-0": return "0"
		else: return strRPM

	def getSpeed(self):
		r = (ConfigSettings.loadRadius, ConfigSettings.loadRadius * 0.393701)[ConfigSettings.metric] # r is always in inches
		currentSpeed = (0.00595 * self.getRPM() * r) * (1, 1.609344)[ConfigSettings.metric]
		return min(currentSpeed, 99)

	def getSpeedString(self):
		strSpeed = str(round(self.getSpeed()))[:-2]
		if strSpeed == "-0": return "0"
		else: return strSpeed

	def getBatteryPercent(self):
		return self.battery

	def getTime(self):
		return self.time

	def updateSensorsHighPriority(self):
		self.time 			= str(datetime.now().time())[:-2]

	def updateSensorsMediumPriority(self):
		self.rpm 			= self.rpm + random() * 2.0 - 1.0

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


class ModeWidget(QAbstractButton):
	def __init__(self, text, parent = 0):
		QWidget.__init__(self, parent)
		self.setText(text)
		self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
		self.fontText = QFont("Liberation Mono")
		self.setCheckable(True)

	def paintEvent(self, e):
		clientrect 			= QRect(0, 0, self.width(), self.height())
		dc 					= QPainter(self)

		dc.setFont(self.fontText)

		if self.isChecked():
			dc.fillRect(clientrect, QColor(200, 200, 200))
			dc.setPen(QColor(0, 0, 0))
		else:
			dc.setPen(QColor(200, 200, 200))
			dc.drawRect(QRect(clientrect.x(), clientrect.y(), clientrect.width() - 1, clientrect.height() - 1))

		dc.drawText(clientrect, Qt.AlignCenter | Qt.AlignVCenter, self.text())

	def resizeEvent(self, e):
		self.fontText.setPixelSize(self.height() / 3.0)


class SwitcherWidget(QWidget):
	def __init__(self, parent=0):
		QWidget.__init__(self, parent)

		self.btnMap	 		= ModeWidget("MAP", self)
		self.btnWire 		= ModeWidget("WIRE", self)
		self.hLayout		= QHBoxLayout(self)

		self.btnMap.setChecked(True)

		self.hLayout.addWidget(self.btnMap)
		self.hLayout.addWidget(self.btnWire)

		QObject.connect(self.btnMap, SIGNAL("clicked()"), self.modeMap)
		QObject.connect(self.btnWire, SIGNAL("clicked()"), self.modeWire)

		self.setLayout(self.hLayout)

	def modeMap(self):
		self.btnMap.setChecked(True)
		self.btnWire.setChecked(False)

	def modeWire(self):
		self.btnMap.setChecked(False)
		self.btnWire.setChecked(True)

#	def paintEvent(self, e):
#		clientrect 			= QRect(0, 0, self.width(), self.height())
#		dc 					= QPainter(self)


class WiringWidget(QWidget):
	def __init__(self, parent=0):
		QWidget.__init__(self, parent)
		self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

		## fonts
		self.fontStats 		= QFont('Liberation Mono')
		self.fontValues		= QFont('Liberation Sans Narrow')

		## styles
		self.dottedLine 	= QPen(ConfigSettings.brightMono, 1, Qt.DotLine)
		self.solidLine		= QPen(ConfigSettings.darkMono, 1)

	def paintEvent(self, e):
		clientrect 			= self.getClientRect()
		dim 				= clientrect.height()
		pad 				= dim / 40
		dc 					= QPainter(self)

		dc.setRenderHint(QPainter.TextAntialiasing, ConfigSettings.textAntialiasing)
		dc.setRenderHint(QPainter.Antialiasing, ConfigSettings.lineAntialiasing)

		## create timing graph
		fmTickValues		= QFontMetrics(self.fontValues)
		gridSteps 			= 11
		strTickUnit 		= "A"
		pxTickMaxStrW		= fmTickValues.width("-" + str(round(float(ConfigSettings.motorCurrent))) + " " + strTickUnit) + 2
		pxTickMaxStrH		= fmTickValues.height()
		rcTimingGrid 		= QRect(clientrect.width() / 10.0 + clientrect.left(), (clientrect.height() / 2.0) + clientrect.top() + pad * 2.0, clientrect.width() * 0.80, clientrect.height() / 2.0 - pad)
		rcTimingRange		= QRect(rcTimingGrid.x() + pad + pxTickMaxStrW, rcTimingGrid.y(), rcTimingGrid.width() - pad - pxTickMaxStrW, rcTimingGrid.height() - pad - pxTickMaxStrH)
		pathTimingRange		= QPainterPath()

		## draw the range lines
		dc.setPen(self.dottedLine)
		pathTimingRange.moveTo(rcTimingRange.x(), rcTimingRange.y())
		pathTimingRange.lineTo(rcTimingRange.x(), rcTimingRange.bottomLeft().y())
		pathTimingRange.moveTo(rcTimingRange.x(), rcTimingRange.center().y())
		pathTimingRange.lineTo(rcTimingRange.bottomRight().x(), rcTimingRange.center().y())

		## draw y-axis tick marks & values
		dc.setFont(self.fontValues)
		for yy in range(0, gridSteps):
			tickValue 		= round((float(yy) / float(gridSteps - 1) * 2) * ConfigSettings.motorCurrent, 1) - ConfigSettings.motorCurrent
			pxTickY 		= float(rcTimingRange.y()) + float(gridSteps - yy - 1) * float((rcTimingRange.height())) / float(gridSteps - 1) - 1
			strAmps			= str(tickValue) + " " + strTickUnit

			fmTickValues.width(strAmps)
			pathTimingRange.moveTo(rcTimingGrid.x() + pxTickMaxStrW, pxTickY)
			pathTimingRange.lineTo(rcTimingRange.x(), pxTickY)

			dc.drawText(QRect(rcTimingGrid.x(), pxTickY - pxTickMaxStrH / 2, pxTickMaxStrW - 2, pxTickMaxStrH), Qt.AlignVCenter | Qt.AlignRight, strAmps)

		## these are dotted so we don't want them to have AA
		dc.setRenderHint(QPainter.Antialiasing, False)
		dc.drawPath(pathTimingRange)
		dc.setRenderHint(QPainter.Antialiasing, ConfigSettings.lineAntialiasing)

		## plot sine waves
		for phase in range(0, 3):
			pathPhaseOutput = QPainterPath()
			degPhaseOffset	= phase * 120.0

			pxRangeLower	= rcTimingRange.x()
			pxRangeUpper 	= rcTimingRange.x() + rcTimingRange.width()
			pxRange 		= pxRangeUpper - pxRangeLower
			firstPoint		= True
			for xx in range(pxRangeLower + 1, pxRangeUpper, 3):
				degPhase 	= (float(xx - pxRangeLower + 1) / float(pxRange) * 360.0) + degPhaseOffset
				rdPhase		= degPhase * math.pi / 180.0
				amplitude 	= -math.sin(rdPhase) * rcTimingRange.height() / 2.0

				if firstPoint == True:
					pathPhaseOutput.moveTo(xx, rcTimingRange.center().y() + amplitude)
					firstPoint = False

				pathPhaseOutput.lineTo(xx, rcTimingRange.center().y() + amplitude)

			## disabled: Fill in the paths with a translucent brush (doesn't look all that great)
			# brFill			= QColor(ConfigSettings.coilColorsBright[phase].red(), ConfigSettings.coilColorsBright[phase].green(), ConfigSettings.coilColorsBright[phase].blue(), 100)
			# pathPhaseOutput.lineTo(rcTimingRange.topRight().x(), rcTimingRange.center().y())
			# dc.fillPath(pathPhaseOutput, brFill)

			dc.setPen(ConfigSettings.coilColorsBright[phase])
			dc.drawPath(pathPhaseOutput)

		## create coil wiring diagram
		rcCoil				= QRectF(rcTimingGrid.center().x() - (dim / 30.0) - pad * 3.0, clientrect.y() + pad * 2, rcTimingGrid.width(), rcTimingGrid.height() - pad * 2.0)
		dimCoil 			= min(rcCoil.width(), rcCoil.height())
		dimInner			= dimCoil * 0.8
		dimSecondary		= dimCoil * 0.96
		dimTraces			= [dimCoil * 1.15, dimCoil * 1.10, dimCoil * 1.05]
		rcCoilSquare		= QRectF(rcCoil.left(), rcCoil.y(), dimCoil, dimCoil)
		rcCoilInner			= QRectF(rcCoilSquare.center().x() - dimInner / 2, rcCoilSquare.center().y() - dimInner / 2, dimInner, dimInner)
		rcCoilSecondary		= QRectF(rcCoilSquare.center().x() - dimSecondary / 2, rcCoilSquare.center().y() - dimSecondary / 2, dimSecondary, dimSecondary)
		rcOuterTraces		= [QRectF(rcCoilSquare.center().x() - dimTraces[0] / 2, rcCoilSquare.center().y() - dimTraces[0] / 2, dimTraces[0], dimTraces[0]),
							   QRectF(rcCoilSquare.center().x() - dimTraces[1] / 2, rcCoilSquare.center().y() - dimTraces[1] / 2, dimTraces[1], dimTraces[1]),
							   QRectF(rcCoilSquare.center().x() - dimTraces[2] / 2, rcCoilSquare.center().y() - dimTraces[2] / 2, dimTraces[2], dimTraces[2])]
		degSpacer			= (10.0 / ConfigSettings.motorCoils)
		degCoilInterval		= (360.0 / ConfigSettings.motorCoils)
		degPhaseSpan		= degCoilInterval * 3
		degTraceSpacer		= 1.7

		for phase in range(0, 3):
			pathCoil		= QPainterPath()
			degCoilSpan		= degCoilInterval - (degSpacer * ConfigSettings.motorCoils)
			degPhaseOffset	= degCoilInterval * (2-phase)

			pathCoil.arcMoveTo(rcCoilSquare, degPhaseOffset)
			ptOutputTrace 	= QPointF(rcCoilSquare.topRight().x() + phase * (dim / 30.0) + (dim / 60.0), rcCoilSquare.topRight().y())
			pxWireStartX	= rcCoilSquare.topRight().x() + dim / 6
			pxWireStartY	= round(rcCoilSquare.topRight().y() + (phase + 0.5) * (dim / 30) + 1)
			radWireStart 	= dim / 60

			## start with the 3-phase input lines
			pathCoil.moveTo(pxWireStartX, pxWireStartY)
			pathCoil.lineTo(ptOutputTrace.x(), pxWireStartY)

			## start adding the paths for the coil wraps
			for magnet in range(0, ConfigSettings.motorCoils / 3):
				degMagnetOffset = degPhaseOffset - degPhaseSpan * magnet
				pathCoil.arcTo(rcCoilSquare, degMagnetOffset, -degCoilSpan)
				pathCoil.arcTo(rcCoilInner, degMagnetOffset - degCoilSpan, 0)
				pathCoil.arcTo(rcCoilInner, degMagnetOffset - degCoilSpan, degCoilSpan)
				pathCoil.arcTo(rcCoilSecondary, degMagnetOffset, 0)
				pathCoil.arcTo(rcCoilSecondary, degMagnetOffset, -degCoilSpan + degTraceSpacer)
				if magnet != ConfigSettings.motorCoils / 3 - 1:
					pathCoil.arcTo(rcOuterTraces[phase], degMagnetOffset - degCoilSpan + degTraceSpacer, 0)
					pathCoil.arcTo(rcOuterTraces[phase], degMagnetOffset - degCoilSpan + degTraceSpacer, -degPhaseSpan + degCoilSpan - degTraceSpacer)

			pathCoil.lineTo(rcCoilSquare.center())

			## draw the wiring paths and terminal connectors for each coil
			dc.setPen(ConfigSettings.coilColorsBright[phase])
			dc.drawPath(pathCoil)
			dc.drawEllipse(pxWireStartX - radWireStart / 2, pxWireStartY - radWireStart / 2, radWireStart, radWireStart)

		dc.setPen(Qt.gray)
		dc.drawEllipse(rcCoilSquare.center().x() - radWireStart / 2, rcCoilSquare.center().y() - radWireStart / 2, radWireStart, radWireStart)

		## draw motor stats
		# TODO: Add other raw sensor data here as well
		strMotorStats = "%d Coils\n" \
						"%dV, %dA" \
						% tuple([ConfigSettings.motorCoils, ConfigSettings.motorVoltage, ConfigSettings.motorCurrent])

		dc.setFont(self.fontStats)
		dc.drawText(QRect(rcTimingGrid.x(), rcCoilSquare.y(), self.width(), rcCoilSquare.height()), Qt.AlignLeft | Qt.AlignBottom, strMotorStats)

	def getClientRect(self):
		dim = min(self.width(), self.height())
		return QRect((self.width() - dim) / 2, (self.height() - dim) / 2, dim, dim)

	def resizeEvent(self, e):
		dim = min(self.width(), self.height())
		self.fontValues.setPixelSize(dim / 28)
		self.fontStats.setPixelSize(dim / 25)


class SensorWidget(QWidget):
	def __init__(self, parent=0):
		QWidget.__init__(self, parent)
		self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

		self.sensors 			= SensorData()

		## tweak colors to your preference
		self.penBattOutline		= QPen(ConfigSettings.brightMono, 2)

		## fonts
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
		self.timerMedium.timeout.connect(self.updateMediumPriority)
		self.timerLow.timeout.connect(self.updateLowPriority)
		self.timerVeryLow.timeout.connect(self.updateVeryLowPriority)

		self.timerHigh.start(10)
		self.timerMedium.start(600)
		self.timerLow.start(2000)
		self.timerVeryLow.start(2 * 60 * 2000) # 2 minutes

	def updateHighPriority(self):
		self.sensors.updateSensorsHighPriority()
		self.repaint()

	def updateMediumPriority(self):
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

		dc.setRenderHint(QPainter.Antialiasing, ConfigSettings.lineAntialiasing)
		dc.setRenderHint(QPainter.TextAntialiasing, ConfigSettings.textAntialiasing)
		dc.setPen(ConfigSettings.brightMono)

		## draw odometer
		strSpeed 		= (self.sensors.getSpeedString(), self.sensors.getRPMString())[ConfigSettings.showRPM]
		strSpeedUnit 	= ("mph", "kph")[ConfigSettings.metric]
		strSpeedUnit	= (strSpeedUnit, "rpm")[ConfigSettings.showRPM]

		dc.setFont(self.fontSpeed)
		fmSpeed 		= QFontMetrics(self.fontSpeed)
		fmSpeedUnit		= QFontMetrics(self.fontSpeedUnit)
		pxSpeedW 		= fmSpeed.width(strSpeed)
		pxSpeedH 		= fmSpeed.height()
		pxSpeedUnitW	= fmSpeedUnit.width(strSpeedUnit)
#		pxSpeedUnitH	= fmSpeedUnit.height()
		rcSpeedUnit		= QRect(clientrect.center() + QPoint(pxSpeedW / 2, -pxSpeedH / 2 - fmSpeed.descent() + fmSpeedUnit.descent()), QSize(pxSpeedUnitW, pxSpeedH))

		dc.drawText(clientrect, Qt.AlignCenter, strSpeed)
		dc.setFont(self.fontSpeedUnit)
		dc.drawText(rcSpeedUnit, Qt.AlignBottom, strSpeedUnit)

		## draw battery meter
#		sizeBattery		= QSize(clientrect.width() / 8, clientrect.height() / 32)
#		rcBattery		= QRect(clientrect.center() - QPoint(sizeBattery.width() / 2, (pxSpeedH - sizeBattery.height()) / 2 + pad), sizeBattery)

		# TODO: Finish this, it looks awful as-is:
		# dc.drawRect(rcBattery)
		# dc.fillRect(rcBattery, ConfigSettings.darkMono)

		## draw current time
		fmTime			= QFontMetrics(self.fontTime)
		rcTimeText 		= QRect(clientrect.left(), clientrect.center().y() + (pxSpeedH / 2) - fmSpeed.descent() + pad, clientrect.width(), fmTime.height())
		rcDateText 		= QRect(clientrect.left(), rcTimeText.bottomRight().y(), clientrect.width(), fmTime.height())

		dc.setFont(self.fontTime)
		dc.setPen(ConfigSettings.darkMono)
		dc.drawText(rcTimeText, Qt.AlignCenter, str(self.sensors.getTime()))
		dc.drawText(rcDateText, Qt.AlignCenter, str(self.sensors.getDate()))

		## draw speed warning for speeds over safe limit
		if not ConfigSettings.showRPM and self.sensors.isSpeedDangerous():
			strSlow		= "SLOW"
			strDown		= "DOWN"
			fmSlowDown	= QFontMetrics(self.fontSlowDown)
			pxSlowDownW	= max(fmSlowDown.width(strSlow), fmSlowDown.width(strDown))
			pxSlowDownH = pxSpeedH - fmSpeed.descent() * 4
			rcSlowDown	= QRect(clientrect.center() - QPoint(pxSlowDownW + pxSpeedW / 2, pxSlowDownH / 2), QSize(pxSlowDownW, pxSlowDownH))

			dc.setFont(self.fontSlowDown)
			dc.setPen(ConfigSettings.brightMono)
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
#		rcMagOuter		= QRectF(clientrect.center().x() - radMagOuter / 2, clientrect.center().y() - radMagOuter / 2, radMagOuter, radMagOuter)
		rcMagInner		= QRectF(clientrect.center().x() - radMagInner / 2, clientrect.center().y() - radMagInner / 2, radMagInner, radMagInner)
#		fmSlipTicks		= QFontMetrics(self.fontSlipTicks)
		degSpacer		= (5.5 / ConfigSettings.motorCoils, 0.0)[ConfigSettings.motorCoils >= 60]
		degCoilInterval	= (360.0 / ConfigSettings.motorCoils)
		degCoilSpan		= degCoilInterval - (degSpacer * ConfigSettings.motorCoils)

		## Draw coil slip, and then magnetic field strength
		nCoil = 0
		for coil in self.sensors.coils:
			nPath 				= nCoil % 3
			pathSlip 			= QPainterPath()
			pathSlipGrid		= QPainterPath()
			pathField 			= QPainterPath()

			pathSlip.arcMoveTo(rcSlipOuter, nCoil * degCoilInterval)
			pathSlip.arcTo(rcSlipOuter, nCoil * degCoilInterval, -degCoilSpan)
			pathSlip.arcTo(rcSlipInner, nCoil * degCoilInterval - degCoilSpan, 0)
			pathSlip.arcTo(rcSlipInner, nCoil * degCoilInterval - degCoilSpan, degCoilSpan)
			pathSlip.closeSubpath()

			## disabled: change the brush and font for tick values
			# dc.setPen(ConfigSettings.coilColors[nPath])
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

			dc.setPen(QPen(ConfigSettings.coilColorsDark[nPath], 1, Qt.DotLine))
			dc.drawPath(pathSlipGrid)
			dc.setPen(ConfigSettings.coilColorsBright[nPath])
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

			dc.setPen(ConfigSettings.magPower)
			dc.fillPath(pathField, ConfigSettings.magPowerDark)
			dc.drawPath(pathField)

			nCoil += 1

	def getClientRect(self):
		dim = min(self.width(), self.height())
		return QRect((self.width() - dim) / 2, (self.height() - dim) / 2, dim, dim)

	def resizeEvent(self, e):
		dim = min(self.width(), self.height())

		## resize fonts
		if ConfigSettings.showRPM: self.fontSpeed.setPixelSize(dim / 5)
		else: self.fontSpeed.setPixelSize(dim / 3)

		self.fontSpeedUnit.setPixelSize(dim / 18)
		self.fontSlowDown.setPixelSize(dim / 24)
		self.fontSlipTicks.setPixelSize(dim / 30)
		self.fontTime.setPixelSize(dim / 20)

	def mouseReleaseEvent(self, e):
		ConfigSettings.showRPM = not ConfigSettings.showRPM
		self.resizeEvent(e)

class MainWindow(QMainWindow):
	def __init__(self, *args):
		QMainWindow.__init__(self, *args)
		self.wnd 		= QWidget(self)
		self.setCentralWidget(self.wnd)

		self.sensors 	= SensorWidget(self.wnd)
		self.wiring 	= WiringWidget(self.wnd)
		self.switcher 	= SwitcherWidget(self.wnd)

		self.hLayout 	= QHBoxLayout()
		self.hLayout.setSpacing(0)
		self.hLayout.setContentsMargins(0, 0, 0, 0)
		self.hLayout.addWidget(self.sensors)
		self.hLayout.addWidget(self.wiring)

		self.vLayout	= QVBoxLayout()
		self.vLayout.setSpacing(0)
		self.vLayout.setContentsMargins(0, 0, 0, 0)
		self.vLayout.addLayout(self.hLayout, 5)
		self.vLayout.addWidget(self.switcher, 1)

		self.wnd.setLayout(self.vLayout)


class BikeHudApp(QApplication):
	def __init__(self, *args):
		QApplication.__init__(self, *args)

		pal = self.palette()
		pal.setColor(QPalette.Background, ConfigSettings.background)
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
