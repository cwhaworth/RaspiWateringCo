import json, time
import RPi.GPIO as GPIO
from datetime import date
from datetime import datetime


GPIO.setmode(GPIO.BCM)
#log file to read forcast from
log = open("/var/www/FlaskServer/static/forecast.txt", "r")
fcast = log.readlines()
fcastToday = ""
log.close()

for line in fcast:
	#extract forecast reference_time and status from file read
	reftime = line.find("reference_time=")
	refstatus = line.find("status=")
	reftimeend = line.find("+")
	refstatend = line.find(", d")

	fcastTime = line[reftime : reftimeend]
	status = line[refstatus : refstatend]
	fcastTime = fcastTime.replace("reference_time=", "")
	status = status.replace("status=", "")

	#isolate system date, and forecast time
	foreDate = fcastTime[8 : 10]
	foreHour = fcastTime[11 : 13]
	today = str(date.today())
	today = today[8 : 10]
#	today = '16'

	if foreDate == today:
		fcastToday += str(fcastTime) + ", " + str(status) + "\n"
#print(f'forecast:\n{fcastToday}')

#perform, and log actions
log = None
with open('/var/www/FlaskServer/static/water-log.json', 'r') as f:
	log = json.load(f)
sectData = None
with open('/var/www/FlaskServer/static/watering-sectors.json', 'r') as f:
	sectData = json.load(f)
now = datetime.now()

#if it rains: reset last-rained, and write to log
if fcastToday != '' and "rain" in fcastToday:
	newLog = {'date': f'{now.strftime("%m/%d/%Y")}',
		'time': f'{now.strftime("%H:%M:%S")}',
		'message': f'Did not water, because it rained today.'

	}
	log['log'].append(newLog)
	with open('/var/www/FlaskServer/static/water-log.json', 'w') as f:
		json.dump(log, f, indent=2, sort_keys=True)

	sectData["last-rained"] = 0
	with open('/var/www/FlaskServer/static/watering-sectors.json', 'w') as f:
		json.dump(sectData, f, indent=2, sort_keys=True)

#if it does not rain: water sectors based on interval
elif fcastToday != '':
	sectData["last-rained"] += 1
	line = "Watered sector(s): "

	pump = sectData['pump-pin']

	GPIO.setup(pump, GPIO.OUT)
	GPIO.output(pump, GPIO.LOW)
	time.sleep(1)
	for sector in sectData["sector"]:
		if sector["rain-inc"] <= sectData["last-rained"] and sectData["last-rained"] % sector["rain-inc"] == 0:
			GPIO.setup(sector['pin'], GPIO.OUT)
			GPIO.output(sector['pin'], GPIO.LOW)
			line += str(sector["id"]) + ", "
	time.sleep(4)

	GPIO.cleanup(pump)
	time.sleep(1)
	for sector in sectData['sector']:
		if sector['rain-inc'] <= sectData['last-rained'] and sectData['last-rained'] % sector['rain-inc'] == 0:
			GPIO.cleanup(sector['pin'])

	line = line[ : -2]
	newLog = {'date': f'{now.strftime("%m/%d/%Y")}',
		'time': f'{now.strftime("%H:%M:%S")}',
		'message': line
	}
	log['log'].append(newLog)
	with open('/var/www/FlaskServer/static/water-log.json', 'w') as f:
		json.dump(log, f, indent=2, sort_keys=True)

	with open('/var/www/FlaskServer/static/watering-sectors.json', 'w') as f:
		json.dump(sectData, f, indent=2, sort_keys=True)

#if get forecast operation returned erroneous
else:
	newLog = {'date': f'{now.strftime("%m/%d/%Y")}',
		'time': f'{now.strftime("%H:%M:%S")}',
		'message': "Forecast data was not initialized correctly. Check for errors in 'forecast.txt'."
	}
	log['log'].append(newLog)
	with open('/var/www/FlaskServer/static/water-log.json', 'w') as f:
		json.dump(log, f, indent=2, sort_keys=True)

	sectData["last-rained"] += 1
	with open('/var/www/FlaskServer/static/watering-sectors.json', 'w') as f:
		json.dump(sectData, f, indent=2, sort_keys=True)
