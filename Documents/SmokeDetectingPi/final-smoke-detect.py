import time
import botbook_mcp3002 as mcp
import os
import glob
import subprocess
import calendar
import urllib2
import json
import time
from google.cloud import storage
import RPi.GPIO as GPIO
import time
import datetime
from firebase.firebase import FirebaseApplication, FirebaseAuthentication
from firebase import firebase

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) #(GPIOport, out)
pwm = GPIO.PWM(17, 50) 
pwm.start(7.5)
'''
os.system('sudo service ddclient start')
os.system('sudo chmod +x /etc/cron.weekly/ddclient')
os.system('sudo ddclient -daemon=0 -debug -verbose -noquiet') 
'''
url = 'https://smoke-detecting.firebaseio.com/notifications.json'
smokeLevel = 0

fb = firebase.FirebaseApplication('https://smoke-detecting.firebaseio.com', None)

time2 = ""
resultsv = ""
oldresultsv = fb.get('/servo/value', None)

resultpic = '0'
resultcam = 0


#read channel 0 on device 0           
while True:

	#check_start_camera
	resultcam = fb.get('/startcamera/value', None)
	if resultcam == 1:
		os.system('sudo service motion start') 	
	else:
		os.system('sudo service motion stop')		
	
	#check_data_in_firebase finish
	resultsv = fb.get('/servo/value', None)		
	if resultsv != oldresultsv:
		oldresultsv = resultsv
		pwm.ChangeDutyCycle(oldresultsv)
		time.sleep(1)
		
	#take_picture finish	
	resultpic = str(fb.get('/takepicture/value', None))
	resultid = str(fb.get('/id/value', None))	
	if resultpic != '0':
		os.system('sudo service motion stop')		
		picnum = str(fb.get('/notifications/'+resultid+'/picnum',None))				
		picnum2 = int(picnum)
		picnum2 = picnum2+1
		picnum3 = str(picnum2)
		os.system('sudo fswebcam -s 30 '+picnum3+'.jpg')			
		client = storage.Client()
		bucket = client.get_bucket('smoke-detecting.appspot.com')
		blob = bucket.blob('uploadpic/'+resultpic+'/'+picnum3+'.jpg')
		blob.upload_from_filename(filename='/home/pi/Documents/'+picnum3+'.jpg')
		
		resultpic = '0'	
		FIREBASE_URL = "https://smoke-detecting.firebaseio.com"
		fb = firebase.FirebaseApplication(FIREBASE_URL, None)	
		fb.put('/takepicture', "value", '0')			
		os.system('sudo service motion start')	
	
	#detect smoke finish	
	value2 = mcp.readAnalog(0, 0)
	print ("value 2 : %i" % value2)
	if value2 > 300:
		print ('smoke detected!')
			
		time2 = str(calendar.timegm(time.gmtime()))
		#send_dectect_data_to_firebase
		postdata = {
			'date': time2,
			'dataMQ2': str(value2),
			'datetime': "",
			'picnum' : "5"
		}
		req = urllib2.Request(url)
		data = json.dumps(postdata)
		response = urllib2.urlopen(req,data,timeout=30)
		print 'data have sent!!'
			
			
			
			
		#five_picture()	finish		
		try: 			
			os.system('sudo service motion stop')	
			j=1
			for i in range(2, 12):		
				if i == 2 or i == 4 or i == 6 or i == 8 or i == 11:
					pwm.ChangeDutyCycle(i)
					time.sleep(1)				
					os.system('sudo fswebcam -s 30 '+str(j)+'.jpg')					
					j+=1	
			for i in range(1, 6):						
				client = storage.Client()
				bucket = client.get_bucket('smoke-detecting.appspot.com')
				blob = bucket.blob('uploadpic/'+time2+'/'+str(i)+'.jpg')
				blob.upload_from_filename(filename='/home/pi/Documents/'+str(i)+'.jpg')
				print('Image uploaded successfully')			
			os.system('sudo service motion start') 				
		except KeyboardInterrupt:
			GPIO.cleanup()
			
			for i in range(1, 61):				
				#check_start_camera
				resultcam = fb.get('/startcamera/value', None)
				if resultcam == 1:
					os.system('sudo service motion start') 	
				else:
					os.system('sudo service motion stop')		
	
				#check_data_in_firebase finish
				resultsv = fb.get('/servo/value', None)		
				if resultsv != oldresultsv:
					oldresultsv = resultsv
					pwm.ChangeDutyCycle(oldresultsv)
					time.sleep(1)
			
				#take_picture finish	
				resultpic = str(fb.get('/takepicture/value', None))
				resultid = str(fb.get('/id/value', None))	
				if resultpic != '0':
					os.system('sudo service motion stop')		
					picnum = str(fb.get('/notifications/'+resultid+'/picnum',None))				
					picnum2 = int(picnum)
					picnum2 = picnum2+1
					picnum3 = str(picnum2)
					os.system('fswebcam -s 30 '+picnum3+'.jpg')					
					client = storage.Client()
					bucket = client.get_bucket('smoke-detecting.appspot.com')
					blob = bucket.blob('uploadpic/'+resultpic+'/'+picnum3+'.jpg')
					blob.upload_from_filename(filename='/home/pi/Documents/'+picnum3+'.jpg')
					resultpic = '0'	
					FIREBASE_URL = "https://smoke-detecting.firebaseio.com"
					fb = firebase.FirebaseApplication(FIREBASE_URL, None)	
					fb.put('/takepicture', "value", '0')					
					os.system('sudo service motion start')
	time.sleep(1)			
				
	

	
		
		





