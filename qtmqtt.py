#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtWidgets
import paho.mqtt.client as mqtt
# import PyQt5
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *


# https://github.com/eyllanesc/qtmqtt
# https://stackoverflow.com/questions/52623799/use-paho-mqtt-with-pyqt

class QtMqttClient(QtCore.QObject):
	Disconnected = 0
	Connecting = 1
	Connected = 2

	MQTT_3_1 = mqtt.MQTTv31
	MQTT_3_1_1 = mqtt.MQTTv311

	connected = QtCore.pyqtSignal()
	disconnected = QtCore.pyqtSignal()

	stateChanged = QtCore.pyqtSignal(int)
	hostnameChanged = QtCore.pyqtSignal(str)
	portChanged = QtCore.pyqtSignal(int)
	keepAliveChanged = QtCore.pyqtSignal(int)
	cleanSessionChanged = QtCore.pyqtSignal(bool)
	protocolVersionChanged = QtCore.pyqtSignal(int)

	messageSignal = QtCore.pyqtSignal(str)

	def __init__(self, parent=None):
		super(QtMqttClient, self).__init__(parent)

		self.m_hostname = ""
		self.m_port = 1883
		self.m_keepAlive = 60
		self.m_cleanSession = True
		self.m_protocolVersion = QtMqttClient.MQTT_3_1

		self.m_state = QtMqttClient.Disconnected

		self.m_client = mqtt.Client(clean_session=self.m_cleanSession,
									protocol=self.protocolVersion)

		self.m_client.on_connect = self.on_connect
		self.m_client.on_message = self.on_message
		self.m_client.on_disconnect = self.on_disconnect

	@QtCore.pyqtProperty(int, notify=stateChanged)
	def state(self):
		return self.m_state

	@state.setter
	def state(self, state):
		if self.m_state == state: return
		self.m_state = state
		self.stateChanged.emit(state)

	@QtCore.pyqtProperty(str, notify=hostnameChanged)
	def hostname(self):
		return self.m_hostname

	@hostname.setter
	def hostname(self, hostname):
		if self.m_hostname == hostname: return
		self.m_hostname = hostname
		self.hostnameChanged.emit(hostname)

	@QtCore.pyqtProperty(int, notify=portChanged)
	def port(self):
		return self.m_port

	@port.setter
	def port(self, port):
		if self.m_port == port: return
		self.m_port = port
		self.portChanged.emit(port)

	@QtCore.pyqtProperty(int, notify=keepAliveChanged)
	def keepAlive(self):
		return self.m_keepAlive

	@keepAlive.setter
	def keepAlive(self, keepAlive):
		if self.m_keepAlive == keepAlive: return
		self.m_keepAlive = keepAlive
		self.keepAliveChanged.emit(keepAlive)

	@QtCore.pyqtProperty(bool, notify=cleanSessionChanged)
	def cleanSession(self):
		return self.m_cleanSession

	@cleanSession.setter
	def cleanSession(self, cleanSession):
		if self.m_cleanSession == cleanSession: return
		self.m_cleanSession = cleanSession
		self.cleanSessionChanged.emit(cleanSession)

	@QtCore.pyqtProperty(int, notify=protocolVersionChanged)
	def protocolVersion(self):
		return self.m_protocolVersion

	@protocolVersion.setter
	def protocolVersion(self, protocolVersion):
		if self.m_protocolVersion == protocolVersion: return
		if protocolVersion in (QtMqttClient.MQTT_3_1, MQTT_3_1_1):
			self.m_protocolVersion = protocolVersion
			self.protocolVersionChanged.emit(protocolVersion)

	#################################################################
	@QtCore.pyqtSlot()
	def connectToHost(self):
		if self.m_hostname:
			self.m_client.connect(self.m_hostname,
								  port=self.port,
								  keepalive=self.keepAlive)

			self.state = QtMqttClient.Connecting
			self.m_client.loop_start()

	@QtCore.pyqtSlot()
	def disconnectFromHost(self):
		self.m_client.disconnect()

	def subscribe(self, path):
		if self.state == QtMqttClient.Connected:
			self.m_client.subscribe(path)

	#################################################################
	# callbacks
	def on_message(self, mqttc, obj, msg):
		pp = msg.payload.decode("ascii")
		topic = msg.topic
		mstr = topic+':'+pp
		# print('on_message[{}][{}]'.format( topic,mstr))
		self.messageSignal.emit(mstr)

	def on_connect(self, *args):
		# print("on_connect", args)
		self.state = QtMqttClient.Connected
		self.connected.emit()

	def on_disconnect(self, *args):
		# print("on_disconnect", args)
		self.state = QtMqttClient.Disconnected
		self.disconnected.emit()

################################################################################
################################################################################
################################################################################

class MyMon(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(MyMon, self).__init__(parent)

		lay = QtWidgets.QVBoxLayout(self)
		self.lcd_number = QtWidgets.QLineEdit('AAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBB')
		lay.addWidget(self.lcd_number)

		self.setGeometry(800, 100, 250, 400)

		self.client = QtMqttClient(self)
		self.client.stateChanged.connect(self.on_stateChanged)
		self.client.messageSignal.connect(self.on_messageSignal)
		self.client.hostname = "10.0.0.2"
		self.client.connectToHost()

	@QtCore.pyqtSlot(int)
	def on_stateChanged(self, state):
		if state == QtMqttClient.Connected:
			print(state, 'original')
			self.client.subscribe("pizero-temp")
			self.client.subscribe("lolin-d32-pro")
			self.client.subscribe("room2F")

	@QtCore.pyqtSlot(str)
	def on_messageSignal(self, msg):
		print('test ', msg)
		self.lcd_number.setText(msg)


if __name__ == '__main__':
	import sys

	app = QtWidgets.QApplication(sys.argv)
	w = MyMon()
	w.show()
	sys.exit(app.exec_())
