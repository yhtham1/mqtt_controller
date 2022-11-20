#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtmqtt import QtMqttClient

# QTextLine
# QTextEdit
# QLineEdit

class Test1(QWidget):
	def quit(self):
		print('quit')
		QCoreApplication.quit()

	def __init__(self, parent=None):
		super(Test1, self).__init__(parent)

		qcore = QWidget(self)
		self.mmm = QVBoxLayout(qcore)

		b = QPushButton('Quit')
		b.clicked.connect(self.quit)
		self.mmm.addWidget(b)


		b = QLineEdit('QLineEdit')
		self.mmm.addWidget(b)

		b = QTextEdit('QTextEdit')
		self.mmm.addWidget(b)

		b = QTextLine()
		b = QTextEncoder()




		self.setLayout(self.mmm)
		self.setGeometry(800, 100, 650, 400)

		self.setWindowTitle('Test1 2022-11-20')
		self.show()


def main():
	app = QApplication(sys.argv)
	ex = Test1()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
