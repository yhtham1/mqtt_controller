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
import sys
import re


def ext_from(s1):
	ans = ''
	##########################################
	# x = str1.find(':')
	# ans = str1[:x]
	pattern = re.compile(r"([a-zA-Z0-9-]+):.*")
	m = pattern.match(s1)
	if m:
		ans = m.group(1)


	print('IN :{}'.format(s1))
	print('OUT:{}'.format(ans))
	return ans


def ext_press(s1):
	ans = ''
	##########################################
	# pattern = re.compile(r".*\(\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2}\).*")
	pattern = re.compile(r" pres:(\d{3,4}.\d{2}) ")
	m = pattern.search(s1)
	if m:
		ans = m.group(1)
	return ans


def ext_temp(s1):
	ans = ''
	##########################################
	# pattern = re.compile(r".*\(\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2}\).*")
	pattern = re.compile(r" temp:(\d{2}.\d{2}) ")
	m = pattern.search(s1)
	if m:
		ans = m.group(1)
	return ans


def ext_datetime(s1):
	ans = ''
	##########################################
	pattern = re.compile(r"date:(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ")
	m = pattern.search(s1)
	if m:
		ans = m.group(1)
		return ans
	return ans


def ext_since(s1):
	ans = ''
	##########################################
	pattern = re.compile(r".*since:(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*")
	m = pattern.search(s1)
	if m:
		ans = m.group(1)
		return ans
	return ans


def ext_paras(a):
	from1 = ext_from(a)
	date1 = ext_datetime(a)
	pres1 = ext_press(a)
	temp1 = ext_temp(a)
	since1 = ext_since(a)
	# print('[{}] -> [{}]'.format(a, ans),end='')
	return from1, date1, pres1, temp1, since1


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
		brokerip = '10.0.0.2'
	return brokerip

# def CheckWord(txt, keyw):
# 	ans = txt.split()
# 	p = ans[0].find(keyw)
# 	if 0 > p:
# 		return None
# 	ans = txt.split()
# 	return ans


class MQTTMonitor(QWidget):

	def __init__(self, parent=None):
		super(MQTTMonitor, self).__init__(parent)
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
		grp_name, date1, pres1, temp1, since1 = ext_paras(msg)
		# print('from[{}]'.format(grp_name))
		x = self.findChild(QGroupBox, grp_name)
		if None != x:
			lbl1 = x.findChild(QLabel, 'TEMP')
			if None != lbl1:
				lbl1.setText(temp1)
			lbl1 = x.findChild(QLabel, 'DATE')
			if None != lbl1:
				lbl1.setText(date1)
			lbl1 = x.findChild(QLabel, 'PRES')
			if None != lbl1:
				lbl1.setText(pres1)
			lbl1 = x.findChild(QLabel, 'SINCE')
			if None != lbl1:
				lbl1.setText(since1)
		return

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
		make_h('TEMP', h)
		make_h('DATE', h)
		v.addLayout(h)
		h = QHBoxLayout()
		make_h('PRES', h)
		make_h('SINCE', h)
		v.addLayout(h)
		g = QGroupBox(title)
		g.setObjectName(title)  # オブジェクト検索のキーワードになる。
		g.setLayout(v)
		return g

	def quit(self):
		print('quit')
		QCoreApplication.quit()

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

		g = self.make_grp('chime-status')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		g = self.make_grp('esp8266-status')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		g = self.make_grp('camera-status')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		g = self.make_grp('pizero-temp')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		g = self.make_grp('room2F')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		g = self.make_grp('lolin-d32-pro')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		g = self.make_grp('lamp-status')
		self.mmm.addWidget(g)
		self.uidb.append(g)

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

		self.setWindowTitle('MQTT CONTROLLER 2021-12-26')
		self.show()


def pub1(topic, msg):
	# 自分のIPからブローカーを推測する。
	a = get_ip('8.8.8.8')
	brokerip = a
	if 0 <= a.find('192.'):
		brokerip = '192.168.0.17'
	if 0 <= a.find('10.'):
		brokerip = '10.0.0.2'

	client = mqtt.Client()  # クラスのインスタンス(実体)の作成
	client.connect(brokerip, 1883, 60)  # 接続先は自分自身
	client.publish(topic, msg)
	client.disconnect()


def main():
	# a = ext_datetime('2021/08/13 19:19:34 26.21C 1004.00hPa CT:    22715')
	# a = 'date:2021-08-13 19:19:34 26.21C 1004.00hPa CT:    22715'
	# ans = ext_datetime(a)
	# print(ans)
	# return
	app = QApplication(sys.argv)
	ex = MQTTMonitor()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
