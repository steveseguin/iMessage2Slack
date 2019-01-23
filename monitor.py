# pip install slackclient

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import imessage
from slackclient import SlackClient
import os
import threading
import time
import sys
from os.path import expanduser
import sqlite3
import datetime

slack_token =  "xoxp-xxxxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
sc = SlackClient(slack_token)

def get_messages_for_recipient(id):
	
	db_path = expanduser("~") + '/Library/Messages/chat.db'
	connection = sqlite3.connect(db_path)
	c = connection.cursor()
	
	#c.execute("SELECT * FROM `handle`")
	#for row in c:
	#	print(row)   ### FIND THE USER ID FOR THE USER YOU WANT
    	
	cc = c.execute("SELECT * FROM `message` INNER JOIN handle h ON h.ROWID=message.handle_id WHERE handle_id=" + str(id) + " ORDER BY date DESC LIMIT 5")
	messages = []
	
	for row in c:
		messages.append([row])
			
	#print(messages)
	connection.close()
	return reversed(messages)


def loop_check():
	lastmsg = ""
	print("Starting")
	while True:
		old=True
		messages = imessage.get_messages_for_recipient(int(10))
		for msg in messages:
			msg=msg[0]
			if lastmsg==msg[0]:
				old=False
				continue
			if old==True:
				continue
			lastmsg=msg[0]
			
			if (type(msg[2])==type(None)):
				sc.api_call(
				"chat.postMessage",
				channel="iMessage",
				text="Unknown message"
				)
			elif msg[21]!=0:
				sc.api_call(
				"chat.postMessage",
				channel="iMessage",
				text="Me: "+msg[2].encode('utf-8', 'xmlcharrefreplace')
				)
			else:
				sc.api_call(
				"chat.postMessage",
				channel="iMessage",
				text=msg[-5].encode('utf-8', 'xmlcharrefreplace')+": "+msg[2].encode('utf-8', 'xmlcharrefreplace')
				)
		time.sleep(2) ## CHECK EVERY COUPLE SECONDS
		try:
			lastmsg=msg[0]
		except:
			pass

loop_check()




