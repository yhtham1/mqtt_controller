#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import paho.mqtt.client as mqtt
import socket

def get_ip(server_ip):
	#server_ipに接続してそのときのローカルＩＰを得る
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# try:
	# doesn't even have to be reachable
	s.connect((server_ip, 1))
	IP = s.getsockname()[0]
	# except Exception:
	# 	print('fail get_ip()')
	# 	IP = '127.0.0.1'
	# finally:
	s.close()
	return IP
# MQTT Broker
# MQTT_HOST = "localhost"		# brokerのアドレス
MQTT_HOST = "10.0.0.4"		# brokerのアドレス
MQTT_PORT = 1883			# brokerのport
MQTT_KEEP_ALIVE = 60		# keep alive

# broker接続時
def on_connect(mqttc, obj, flags, rc):
	print("rc: " + str(rc))

#メッセージ受信時
def on_message(mqttc, obj, msg):
	tpc = msg.topic
	pp  = msg.payload.decode('ascii')
	print('[{:15} -- {}]'.format(tpc,pp))

mqttc = mqtt.Client()
mqttc.on_message = on_message  # メッセージ受信時に実行するコールバック関数設定
mqttc.on_connect = on_connect

print('')
print('')
print('')
print('')
print('-----------------------------',MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
print('')
print('')
print('')
print('')
print('')
print('')
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)

sub_title = (
	'lamp',
)
#	'temp1',
#	'esp8266-status',
#	'temp2',
#	'pizero-temp',
#	'lolin-d32-pro',
#	'lamp-status',
#	'camera-status',
#	'room2F',
#	)


for it in sub_title:
	print('subscribe:{}'.format(it))
	mqttc.subscribe(it)        # Topicを購読

mqttc.loop_forever()  # 永久ループ


