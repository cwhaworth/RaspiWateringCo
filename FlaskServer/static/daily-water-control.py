import json, time
import RPi.GPIO as GPIO
from datetime import date, datetime


GPIO.setmode(GPIO.BCM)
today = str(date.today())
today = today[8 : 10]
now = datetime.now()
#today = '14'

def readJson(files):
	fList = []
	for file in files:
		with open(f'/var/www/FlaskServer/static/{file}.json', 'r') as f:
			fList.append(json.load(f))
	return fList[0], fList[1], fList[2]

def writeJson(data):
	for d in data['allData']:
		with open(f'/var/www/FlaskServer/static/{d["file"]}.json', 'w') as f:
			json.dump(d['data'], f, indent=2)

def stripOldLog(log, td, inc):
	logDate = datetime.strptime(log['log'][0]['date'], '%m/%d/%Y')
	subDate = td.date() - logDate.date()
	if subDate.days > inc:
		del log['log'][0]
		return stripOldLog(log, td, inc)
	else
		return log

def finalize(l, l60, sd, files):
	l = stripOldLog(l, now, 30)
	l60 = stripOldLog(l60, now, 60)
	data = {'allData': [{'file': files[0],
			'data': l
			},
			{'file': files[1],
			'data': l60
			},
			{'file': files[2],
			'data': sd
			}]
		}
	writeJson(data)

fcast = None
#log file to read forecast from
with open('/var/www/FlaskServer/static/forecast.json') as f:
	fcast = json.load(f)
fcastToday = ""
for fc in fcast['forecast']:
	day = fc['date'][-2 : ]
	if day == today:
		fcastToday += f"{fc['time']}, {fc['status']}\n"
#print(f'forecast:\n{fcastToday}')

#perform, and log actions
files = ['water-log', 'water-log-60-day', 'watering-sectors']
log, log60, sectData = readJson(files)

#if it rains: reset last-rained, and write to log
if fcastToday != '' and "rain" in fcastToday:
	newLog = {'date': f'{now.strftime("%m/%d/%Y")}',
		'time': f'{now.strftime("%H:%M:%S")}',
		'message': f'Did not water, because it rained today.'

	}
	log['log'].append(newLog)
	log60['log'].append(newLog)
	while len(log) > 30:
		del log[0]
	while len(log60) > 60:
		del log[0]

	sectData['last-rained'] = 0

	finalize(log, log60, sectData, files)

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
	log60['log'].append(newLog)
	finalize(log, log60, sectData, files)

#if get forecast operation returned erroneous
else:
	sectData['last-rained'] += 1
	newLog = {'date': f'{now.strftime("%m/%d/%Y")}',
		'time': f'{now.strftime("%H:%M:%S")}',
		'message': "Forecast data was not initialized correctly. Check for errors in 'forecast.txt'."
	}
	log['log'].append(newLog)
	log60['log'].append(newLog)
	finalize(log, log60, sectData, files)
