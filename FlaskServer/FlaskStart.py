import json, re, time
import RPi.GPIO as GPIO
from datetime import date, datetime
from gpiozero import CPUTemperature
from flask import Flask, jsonify, redirect, render_template, request, url_for
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

@app.route("/")
@app.route("/index", methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		for key in request.form.keys():
			if key == 'waterAll':
				waterAll()
			elif key.startswith('waterNow_'):
				sectID = key.split('_')[1]
				waterNow(int(sectID))

		return redirect(url_for('.index'))
	else:
		navURL = getNavURL()
		styles = getStyles()
		now = datetime.now()
		cpu = CPUTemperature()

		data = {'sectData': None,
			'weather': None,
			'sysData': None,
			'cpuTemp': {
				'time': f'{now.strftime("%H:%M")}',
				'temp': f'{round(cpu.temperature, 1)} C'
			}
		}
		data['sectData'] = getJsonData('watering-sectors')
		data['weather'] = getForecast(getJsonData('forecast'))
		data['sysData'] = getJsonData('system-data')

		return render_template('index.html', navurl=navURL, styles=styles, data=data)

def waterAll():
	sectData = getJsonData('watering-sectors')
	pump = sectData['pump-pin']

	GPIO.setup(pump, GPIO.OUT)
	GPIO.output(pump, GPIO.LOW)
	time.sleep(1)
	for sector in sectData['sector']:
		GPIO.setup(sector['pin'], GPIO.OUT)
		GPIO.output(sector['pin'], GPIO.LOW)
	time.sleep(4)
	GPIO.cleanup(pump)
	time.sleep(1)
	for sector in sectData['sector']:
		GPIO.cleanup(sector['pin'])

	log = getJsonData('water-log')
	log60 = getJsonData('water-log-60-day')
	now = datetime.now()
	newLog = {'date': f'{now.strftime("%m/%d/%Y")}',
		'time': f'{now.strftime("%H:%M:%S")}',
		'message': 'Watered all sectors by manual override.'
	}
	log['log'].append(newLog)
	log60['log'].append(newLog)

	today = getToday()
	log = stripOldLog(log, today, 30)
	log60 = stripOldLog(log60, today, 60)

	setJsonData('water-log', log)
	setJsonData('water-log-60-day', log60)

def waterNow(sectID):
	sectData = getJsonData('watering-sectors')
	pump = sectData['pump-pin']
	sectorTemp = {}
	for sector in sectData['sector']:
		if sector['id'] == sectID:
			sectorTemp = sector
			break

	GPIO.setup(pump, GPIO.OUT)
	GPIO.output(pump, GPIO.LOW)
	time.sleep(1)
	GPIO.setup(sectorTemp['pin'], GPIO.OUT)
	GPIO.output(sectorTemp['pin'], GPIO.LOW)
	time.sleep(4)
	GPIO.cleanup(pump)
	time.sleep(1)
	GPIO.cleanup(sectorTemp['pin'])

	log = getJsonData('water-log')
	log60 = getJsonData('water-log-60-day')
	now = datetime.now()
	newLog = {'date': f'{now.strftime("%m/%d/%Y")}',
		'time': f'{now.strftime("%H:%M:%S")}',
		'message': f'Watered sector {sectID} by manual override.'

	}
	log['log'].append(newLog)
	log60['log'].append(newLog)

	today = getToday()
	log = stripOldLog(log, today, 30)
	log60 = stripOldLog(log60, today, 60)

	setJsonData('water-log', log)
	setJsonData('water-log-60-day', log60)

def getForecast(forecast_json):
	counter = 0
	weather = []
	for fcast in forecast_json['forecast']:
		if counter == 8:
			break
		else:
			weather.append(fcast)
			counter +=1
	return weather

def stripOldLog(log, td, inc):
	logDate = datetime.strptime(log['log'][0]['date'], '%m/%d/%Y')
	subDate = td.date() - logDate.date()
	if subDate.days > inc:
		del log['log'][0]
		return stripOldLog(log, td, inc)
	else:
		return log

@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
	sectData = getJsonData('watering-sectors') navURL = getNavURL() styles = getStyles()

	if request.method == 'POST':
		tempData = {'last-rained': sectData['last-rained'],
			'pump-pin': sectData['pump-pin'],
			'sector':[]
		}
		sectID = request.form.getlist('sectorID')
		sectPin = request.form.getlist('sectorPin')
		sectInc = request.form.getlist('sectorInc')
		for key in request.form.keys():
			if key.startswith('sectDel_'):
				delSectID = key.split('_')[1]
				for i in range(len(sectID)):
					sectTemp = {'id': int(sectID[i]),
						'pin': int(sectPin[i]),
						'rain-inc': int(sectInc[i])
					}
					if sectTemp['id'] != int(delSectID):
						tempData['sector'].append(sectTemp)
				return render_template('initialize.html', navurl=navURL, styles=styles, sectData=tempData)
			elif key == 'sectAdd':
				counter = 0
				for i in range(len(sectID)):
					sectTemp = {'id': int(sectID[i]),
						'pin': int(sectPin[i]),
						'rain-inc': int(sectInc[i])
					}
					counter = i + 1
					tempData['sector'].append(sectTemp)

				empty = {'id': counter + 1,
					'pin': 0,
					'rain-inc': 0

				}
				tempData['sector'].append(empty)
				return render_template('initialize.html', navurl=navURL, styles=styles, sectData=tempData)
			elif key == 'sectInit':
				tempData['pump-pin'] = int(request.form['pumpPin'])
				for i in range(len(sectID)):
					sectTemp = {'id': i + 1,
						'pin': int(sectPin[i]),
						'rain-inc': int(sectInc[i])
					}
					tempData['sector'].append(sectTemp)

				setJsonData('watering-sectors', tempData)
				return redirect(url_for('.initialize'))
		return render_template('initialize.html', navurl=navURL, styles=styles, sectData=sectData)
	else:
		return render_template('initialize.html', navurl=navURL, styles=styles, sectData=sectData)

@app.route("/water-log", methods=['GET', 'POST'])
def waterLog():
	formButtons = True
	if request.method == 'POST':
		if 'clear' in request.form.keys():
			data = {'log': []
			}
			setJsonData('water-log', data)
			return redirect(url_for('.waterLog'))
		if '60daylog' in request.form.keys():
			formButtons = False
			navURL = getNavURL()
			styles = getStyles()
			waterLog = getJsonData('water-log-60-day')
			return render_template('water-log.html', navurl=navURL, styles=styles, waterLog=waterLog, formButtons=formButtons)
		if 'back' in request.form.keys():
			return redirect(url_for('.waterLog'))
	else:
		navURL = getNavURL()
		styles = getStyles()
		waterLog = getJsonData('water-log')
		return render_template('water-log.html', navurl=navURL, styles=styles, waterLog=waterLog, formButtons=formButtons)

def getToday():
	today = datetime.now()
	return today

def getNavURL():
	navURL = {'index': url_for('.index'),
		'init': url_for('.initialize'),
		'waterLog': url_for('.waterLog')
	}

	return navURL

def getStyles():
	styles = url_for('static', filename='styles.css')

	return styles

def getJsonData(filename):
	data = None

	with open(f'static/{filename}.json', 'r') as file:
		data = json.load(file)

	return data

def setJsonData(filename, data):
	with open(f'static/{filename}.json', 'w') as file:
		json.dump(data, file, indent=2, sort_keys=True)

if __name__ == '__main__':
	app.run(debug=True)
