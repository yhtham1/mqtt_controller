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

# NEC照明(RE0208)
re0208data = (
	('ON/OFF','0x41B6D52A'),
	('全灯  ','0x41B6659A'),
	('明    ','0x41B65DA2'),
	('暗    ','0x41B6DD22'),
	('常夜灯','0x41B63DC2'),
	('タイマ','0x41B6F50A'),
	('留守番','0x41B68E98'),
)



tcldata = (


	('入力切替     ','0x34689D3AC5'),
	('電源         ','0x34689DAB54'),
	('地デジ       ', '0x34689DAA55'),
	('BS/CS        ','0x34689DFA05'),
	('4K           ','0x34689DDA25'),
	('CH1          ','0x34689D738C'),
	('CH2          ','0x34689DB34C'),
	('CH3          ','0x34689D33CC'),
	('CH4          ','0x34689DD32C'),
	('CH5          ','0x34689D53AC'),
	('CH6          ','0x34689D936C'),
	('CH7          ','0x34689D13EC'),
	('CH8          ','0x34689DE31C'),
	('CH9          ','0x34689D639C'),
	('CH0          ','0x34689D0AF5'),
	('CH11         ','0x34689D8A75'),
	('CH12         ','0x34689D4AB5'),
	('音量+        ', '0x34689D0BF4'),
	('音量-        ', '0x34689D8B74'),
	('消音         ', '0x34689D03FC'),
	('メニュー設定         ', '0x34689D0CF3'),
	('チャンネル↑ ', '0x34689D4BB4'),
	('チャンネル↓ ', '0x34689DCB34'),
	('機能     ', '0x34689DC837'),
	('ホーム     ', '0x34689DEF10'),
	('録画リスト     ', '0x34689DBA45'),
	('番組表     ', '0x34689DA758'),
	('          ↑ ', '0x34689D659A'),
	('          ↓ ', '0x34689DE51A'),
	('          → ', '0x34689D15EA'),
	('          ← ', '0x34689D956A'),
	('決定         ', '0x34689DD02F'),
	('戻る         ', '0x34689D1BE4'),
	('dデータ     ', '0x34689D9A65'),
	('青           ','0x34689DE41B'),
	('赤           ','0x34689DFF00'),
	('緑           ','0x34689DE817'),
	('黄           ','0x34689DD827'),
	('画面表示     ', '0x34689DC33C'),
	('字幕         ','0x34689DFE01'),
	('音声切替     ','0x34689DA55A'),
	('早戻し       ','0x34689D47B8'),
	('再生         ','0x34689D57A8'),
	('早送り       ','0x34689DC738'),
	('前           ','0x34689DA25D'),
	('一時停止     ','0x34689D6798'),
	('次           ','0x34689D35CA'),
	('録画         ','0x34689D17E8'),
	('3桁入力      ','0x34689DCA35'),
	('停止         ','0x34689D07F8'),
	('NETFLIX      ','0x34689D08F7'),
	('hulu         ','0x34689DA45B'),
	('U-NEXT       ','0x34689D5CA3'),
	('Abema        ','0x34689D3CC3'),
	('YouTube      ','0x34689DB847'),
	('T            ','0x34689D38C7'),
	)


def ext_paras2(a):

	if 0>a.find('\t'):
		print('IN:{}'.format(a))
		return '','','','',''
	# print('IN:{}'.format(a))
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


class PublishConstMessage:
	def __init__(self, topic, msg):
		self.topic = topic
		self.msg = msg

	def __call__(self):
		pub1(self.topic, self.msg)



class MQTTAmp(QWidget):

	def __init__(self, parent=None):
		super(MQTTAmp, self).__init__(parent)


		style = '''
			QWidget1{
				padding:    1px;
				margin:     1px;
				background-color:pink;
			}
			QHBoxLayout{
				margin-top: 0px;
				margin-bottom: 0px;
				margin-left: 2px;
				margin-right: 2px;
			}
			QVBoxLayout{
				margin-top: 0px;
				margin-bottom: 0px;
				margin-left: 2px;
				margin-right: 2px;
			}
			QLineEdit{
				align:right;
				qproperty-alignment: AlignRight;
				border-style: outset;
				border-width:		1px;
				border-color:		red;
				background-color:yellow;
			}
			QPushButton{
				min-height: 50px;
				font-size:  20pt;
			}
			'''
		# self.setStyleSheet(style)


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

	def send_iris(self):
		print('send_iris')
		pass

	def quit(self):
		print('quit')
		QCoreApplication.quit()

	def ledOn(self):
		pub1('lamp', 'white 80')
		pub1('lamp', 'warm 80')

	def ledOff(self):
		pub1('lamp', 'white 0')
		pub1('lamp', 'warm 0')

	def initUI(self):
		qcore = QWidget(self)
		self.mmm = QVBoxLayout(qcore)

		g = self.make_grp('lamp-status')
		self.mmm.addWidget(g)
		self.uidb.append(g)

		b = QPushButton('iris')
		# b.clicked.connect(self.send_iris)
		b.clicked.connect(PublishConstMessage('ir_iris', '2'))
		self.mmm.addWidget(b)
		b = QPushButton('quit')
		b.clicked.connect(self.quit)
		self.mmm.addWidget(b)

		v = QVBoxLayout()
		b = QPushButton('up')
		b.clicked.connect(PublishConstMessage('AMP/UPVOL', '10'))
		v.addWidget(b)

		b = QPushButton('down')
		b.clicked.connect(PublishConstMessage('AMP/DOWNVOL', '10'))
		v.addWidget(b)

		b = QPushButton('0')
		b.clicked.connect(PublishConstMessage('AMP/SETCH', '0'))
		v.addWidget(b)

		b = QPushButton('1')
		b.clicked.connect(PublishConstMessage('AMP/SETCH', '1'))
		v.addWidget(b)

		b = QPushButton('2')
		b.clicked.connect(PublishConstMessage('AMP/SETCH', '2'))
		v.addWidget(b)

		b = QPushButton('3')
		b.clicked.connect(PublishConstMessage('AMP/SETCH', '3'))
		v.addWidget(b)

		b = QPushButton('INIT LCD(1)')
		b.clicked.connect(PublishConstMessage('AMP/INIT', '1'))
		v.addWidget(b)

		b = QPushButton('INIT ATT(2)')
		b.clicked.connect(PublishConstMessage('AMP/INIT', '2'))
		v.addWidget(b)

		b = QPushButton('lamp on')
		b.clicked.connect(self.ledOn)
		v.addWidget(b)

		b = QPushButton('lamp off')
		b.clicked.connect(self.ledOff)
		v.addWidget(b)

		b = QPushButton('chime alarm')
		b.clicked.connect(PublishConstMessage('chime', 'alarm'))
		v.addWidget(b)

		b = QPushButton('fancontrol power')
		b.clicked.connect(PublishConstMessage('fancontrol', 'power'))
		v.addWidget(b)

		b = QPushButton('fancontrol High')
		b.clicked.connect(PublishConstMessage('fancontrol', 'high'))
		v.addWidget(b)

		b = QPushButton('fancontrol Low')
		b.clicked.connect(PublishConstMessage('fancontrol', 'low'))
		v.addWidget(b)

		b = QPushButton('fancontrol Swing')
		b.clicked.connect(PublishConstMessage('fancontrol', 'swing'))
		v.addWidget(b)
		v.addStretch()

		h1 = QHBoxLayout()
		h1.addLayout(v)
		# ------------------------------------------------------
		n = int(len(tcldata))
		lines = 17
		cols = int(n/lines)
		print(n, lines, cols)
		st = 0
		ct = 0
		for i in range(cols):
			v = QVBoxLayout()
			for it in tcldata[ct:ct+lines]:
				b = QPushButton(it[0].strip())
				b.clicked.connect(PublishConstMessage('ir_aeha', it[1]))
				v.addWidget(b)
				ct += 1
			h1.addLayout(v)

		v = QVBoxLayout()
		for it in tcldata[ct:ct+lines]:
			b = QPushButton(it[0].strip())
			b.clicked.connect(PublishConstMessage('ir_aeha', it[1]))
			v.addWidget(b)
			ct += 1
		h1.addLayout(v)




		self.mmm.addLayout(h1)
		# ------------------------------------------------------

		v = QVBoxLayout()
		for it in re0208data:
			b = QPushButton(it[0].strip())
			b.clicked.connect(PublishConstMessage('ir_nec', it[1]))
			v.addWidget(b)
		h1.addLayout(v)

		self.mmm.addStretch()
		self.setLayout(self.mmm)
		# self.setGeometry(800, 100, 650, 400)

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

def keyfuync(p):
	j = int(p[1],16)
	print('keyfunc ', p[0], p[1])
	# print(type(p), len(p), j)
	return j

def test1():
	a = sorted(tcldata,key=keyfuync)
	for it in a:
		print(it)



def main():
	# test1()
	# return
	app = QApplication(sys.argv)
	ex = MQTTAmp()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()