#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtmqtt import QtMqttClient
import re
import socket
import paho.mqtt.client as mqtt


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
	# print('OUT:{}'.format(ans))
	return ans

def ext_word(s1, keyword):
	ans = ''
	if 0<=s1.find(keyword+':'):
		ans = s1[len(keyword)+1:]
	return ans

def ext_paras(a):

	if 0>a.find('\t'):
		print('IN:{}'.format(a))
		return '','','','',''
	print('IN:{}'.format(a))
	# print('IN:{}'.format(a))
	date1=''
	pres1=''
	temp1=''
	since1=''
	x = a.find(':')
	from1 = a[:x]
	t = a[x+1:]
	b = t.split('\t')
	for it in b:
		date1 += ext_word(it,'date')
		pres1 += ext_word(it,'pres')
		temp1 += ext_word(it,'temp')
		since1 += ext_word(it,'since')
	# print('[{}] -> [{}]'.format(a, ans),end='')
	return from1, date1, pres1, temp1, since1


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

# def CheckWord(txt, keyw):
# 	ans = txt.split()
# 	p = ans[0].find(keyw)
# 	if 0 > p:
# 		return None
# 	ans = txt.split()
# 	return ans


class MQTTController(QWidget):
	def __init__(self, parent=None):
		super(MQTTController, self).__init__(parent)
		self.settings = QSettings('mqtt_control.ini',QSettings.IniFormat)
		self.settings.setIniCodec('utf-8')
		self.uidb = []
		self.client = QtMqttClient(self)
		self.client.stateChanged.connect(self.on_stateChanged)
		self.client.messageSignal.connect(self.on_messageSignal)
		self.client.hostname = get_broker_ip()
		self.client.connectToHost()
		qcore = QWidget(self)
		self.mmm = QVBoxLayout(qcore)
		self.initUI()
		self.setLayout(self.mmm)
		self.setWindowTitle('MQTT CONTROLLER 2021-12-29')
		# ------------------------------------------------------------ window位置の再生
		self.settings.beginGroup('window')
		# 初回起動のサイズの指定とか、復元とか
		self.resize(self.settings.value("size", QSize(1024, 768)))
		self.move(self.settings.value("pos", QPoint(0, 0)))
		self.settings.endGroup()
		# ------------------------------------------------------------ window位置の再生
		self.show()


	def closeEvent(self, e):
		# ------------------------------------------------------------ window位置の保存
		self.settings.beginGroup('window')
		self.settings.setValue("size", self.size())
		self.settings.setValue("pos", self.pos())
		self.settings.endGroup()
		self.settings.sync()
		# ------------------------------------------------------------ window位置の保存




	@QtCore.pyqtSlot(int)
	def on_stateChanged(self, state):
		if state == QtMqttClient.Connected:
			print('connected')
			for it in self.uidb:
				t1 = it.title()
				print('subscribe:{}'.format(t1))
				self.client.subscribe(it.title())

	@QtCore.pyqtSlot(str)
	def on_messageSignal(self, msg):
		# print('on_messageSignal:', msg)
		grp_name, datblk = ext_paras2(msg)
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
	# a = ext_datetime('2021/08/13 19:19:34 26.21C 1004.00hPa CT:    22715')
	# a = 'date:2021-08-13 19:19:34 26.21C 1004.00hPa CT:    22715'
	# ans = ext_datetime(a)
	# print(ans)
	# return
	app = QApplication(sys.argv)
	ex = MQTTController()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
