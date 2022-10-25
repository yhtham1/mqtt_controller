#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtmqtt import QtMqttClient
import json
import time
import struct
import pickle

import socket
import paho.mqtt.client as mqtt


def ext_paras2(a):

	if 0>a.find('\t'):
		print('IN:{}'.format(a))
		return '','','','',''
	print('IN:{}'.format(a))
	x = a.find(':')
	from_dev = a[:x]
	t = a[x+1:]
	b = t.split('\t')
	dic1 = {}
	for it in b:
		k = it[:it.find(':')]
		d = it[it.find(':')+1:]
		dic1[k] = d
	return from_dev, dic1

def get_ip(ext_server_ip):
	# server_ipに接続(実際には行わない)してそのときのローカルＩＰを得る
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udpなので接続しないまま
	s.connect((ext_server_ip, 1))
	ip = s.getsockname()[0]
	s.close()
	return ip


def get_broker_ip():
	# 自分のIPからブローカーを推測する。
	a = get_ip('8.8.8.8')
	brokerip = a
	if 0 <= a.find('192.'):
		brokerip = '192.168.0.17'
	if 0 <= a.find('10.'):
		brokerip = '10.0.0.4'
	return brokerip

class MQTTAmp(QWidget):

	def __init__(self, parent=None):
		super(MQTTAmp, self).__init__(parent)
		self.uidb = []
		self.initUI()

		self.client = QtMqttClient(self)
		self.client.stateChanged.connect(self.on_stateChanged)
		self.client.messageSignal.connect(self.on_messageSignal)
		self.client.hostname = get_broker_ip()
		self.client.connectToHost()

	@QtCore.pyqtSlot(int)
	def on_stateChanged(self, state):
		if state == QtMqttClient.Connected:
			print('connected')
			for it in self.uidb:
				t1 = it.title()
				print('subscrime:{}'.format(t1))
				self.client.subscribe(it.title())
		# self.client.subscribe("lolin-d32-pro")
		# self.client.subscribe("room2F")

	@QtCore.pyqtSlot(str)
	def on_messageSignal(self, msg):
		# print('on_messageSignal:', msg)
		grp_name, datblk = ext_paras2(msg)
		# grp_name, date1, pres1, temp1, since1 = ext_paras(msg)
		# print('from[{}]'.format(grp_name))
		x = self.findChild(QGroupBox, grp_name)
		if None != x:
			for it in datblk:
				lbl1 = x.findChild(QLabel, it)
				if None != lbl1:
					lbl1.setText(datblk[it])

	def make_grp(self, title):
		def make_h(title, v):
			h = QHBoxLayout()
			t = QLabel(title)  # 表題用QLabel
			h.addWidget(t)
			t = QLabel('not yet')  # データ値格納用QLabel
			t.setObjectName(title)
			pol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
			t.setSizePolicy(pol)
			h.addWidget(t)
			v.addLayout(h)
			return t
		v = QVBoxLayout()
		h = QHBoxLayout()
		make_h('temp', h)
		make_h('date', h)
		make_h('since', h)
		v.addLayout(h)
		h = QHBoxLayout()
		make_h('pres', h)
		make_h('vbat', h)
		make_h('vbat2', h)
		v.addLayout(h)
		g = QGroupBox(title)
		g.setObjectName(title)  # オブジェクト検索のキーワードになる。
		g.setLayout(v)
		return g

	def quit(self):
		print('quit')
		QCoreApplication.quit()

	def volup(self):
		pub1('AMP/UPVOL', ' ')

	def voldown(self):
		pub1('AMP/DOWNVOL', ' ')

	def ch0(self):
		pub1('AMP/CH', '0')

	def ch1(self):
		pub1('AMP/CH', '1')

	def ledOn(self):
		pub1('lamp', 'white 90')
		pub1('lamp', 'warm 90')

	def ledOff(self):
		pub1('lamp', 'white 0')
		pub1('lamp', 'warm 0')

	def chimeAlarm(self):
		pub1('chime', 'alarm')

	def fanPower(self):
		pub1('fancontrol', 'power')

	def fanHigh(self):
		pub1('fancontrol', 'high')

	def fanLow(self):
		pub1('fancontrol', 'low')

	def fanSwing(self):
		pub1('fancontrol', 'swing')

	def initUI(self):
		qcore = QWidget(self)
		self.mmm = QVBoxLayout(qcore)

		g = self.make_grp('lamp-status')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		b = QPushButton('up')
		b.clicked.connect(self.volup)
		self.mmm.addWidget(b)

		b = QPushButton('down')
		b.clicked.connect(self.voldown)
		self.mmm.addWidget(b)

		b = QPushButton('0')
		b.clicked.connect(self.ch0)
		self.mmm.addWidget(b)

		b = QPushButton('1')
		b.clicked.connect(self.ch1)
		self.mmm.addWidget(b)

		b = QPushButton('quit')
		b.clicked.connect(self.quit)
		self.mmm.addWidget(b)

		b = QPushButton('lamp on')
		b.clicked.connect(self.ledOn)
		self.mmm.addWidget(b)

		b = QPushButton('lamp off')
		b.clicked.connect(self.ledOff)
		self.mmm.addWidget(b)

		b = QPushButton('chime alarm')
		b.clicked.connect(self.chimeAlarm)
		self.mmm.addWidget(b)

		b = QPushButton('fancontrol power')
		b.clicked.connect(self.fanPower)
		self.mmm.addWidget(b)

		b = QPushButton('fancontrol High')
		b.clicked.connect(self.fanHigh)
		self.mmm.addWidget(b)

		b = QPushButton('fancontrol Low')
		b.clicked.connect(self.fanLow)
		self.mmm.addWidget(b)

		b = QPushButton('fancontrol Swing')
		b.clicked.connect(self.fanSwing)
		self.mmm.addWidget(b)

		self.mmm.addStretch()
		self.setLayout(self.mmm)
		self.setGeometry(800, 100, 650, 400)

		self.setWindowTitle('AMP CONTROLLER 2022-10-25')
		self.show()


def pub1(topic, msg):
	# 自分のIPからブローカーを推測する。
	a = get_ip('8.8.8.8')
	brokerip = a
	if 0 <= a.find('192.'):
		brokerip = '192.168.0.17'
	if 0 <= a.find('10.'):
		brokerip = '10.0.0.4'

	client = mqtt.Client()  # クラスのインスタンス(実体)の作成
	client.connect(brokerip, 1883, 60)  # 接続先は自分自身
	client.publish(topic, msg)
	client.disconnect()


def main():
	app = QApplication(sys.argv)
	ex = MQTTAmp()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()