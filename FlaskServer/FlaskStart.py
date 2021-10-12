import json, re, time
import RPi.GPIO as GPIO

from datetime import date, datetime
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

		data = {'sectData': None,
			'weather': None
		}
		data['sectData'] = getSectData()
		forecast_file = open('static/forecast.txt')
		data['weather'] = getForecast(forecast_file)

		return render_template('index.html', navurl=navURL, styles=styles, data=data)

def waterAll():
	sectData = getSectData()
	pump = sectData['pump-pin']

	GPIO.setup(pump, GPIO.OUT)
	GPIO.output(pump, GPIO.HIGH)
	time.sleep(1)

	for sector in sectData['sector']:
		GPIO.setup(sector['pin'], GPIO.OUT)
		GPIO.output(sector['pin'], GPIO.HIGH)
	time.sleep(4)

	GPIO.cleanup(pump)
	time.sleep(1)

	for sector in sectData['sector']:
		GPIO.cleanup(sector['pin'])

	log = open('static/water-log.txt', 'a')
	now = datetime.now()

	log.write(f"{now.strftime('%m/%d/%Y %H:%M:%S')} Watered all sectors by manual override.\n")

def waterNow(sectID):
	sectData = getSectData()
	pump = sectData['pump-pin']

	sectorTemp = {}
	for sector in sectData['sector']:
		if sector['id'] == sectID:
			sectorTemp = sector
			break

	GPIO.setup(pump, GPIO.OUT)
	GPIO.output(pump, GPIO.HIGH)
	time.sleep(1)

	GPIO.setup(sectorTemp['pin'], GPIO.OUT)
	GPIO.output(sectorTemp['pin'], GPIO.HIGH)
	time.sleep(4)

	GPIO.cleanup(pump)
	time.sleep(1)
	GPIO.cleanup(sectorTemp['pin'])

	log = open('static/water-log.txt', 'a')
	now = datetime.now()

	log.write(f"{now.strftime('%m/%d/%Y %H:%M:%S')} Watered sector {sectID} by manual override.\n")

def getForecast(forecast_file):
	fcast = forecast_file.readlines()
	counter = 0
	weather = []

	for line in fcast:

		if counter == 8:
			break
		else:
			reftime = line.find('reference_time=')
			reftimeend = line.find('+')
			refstatus = line.find('status=')
			refstatusend = line.find(', d')

			extractTime = line[reftime : reftimeend]
			extractTime = extractTime.replace('reference_time=', '')
			status = line[refstatus: refstatusend]
			status = status.replace('status=', '')

			date = extractTime[ : 10]
			time = extractTime[11 : ].strip()

			data = {'date': date,
				'time': time,
				'status': status
			}
			weather.append(data)

		counter +=1
	return weather

@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
	sectData = getSectData()
	navURL = getNavURL()
	styles = getStyles()

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

				with open('static/watering-sectors.json', 'w') as file:
					json.dump(tempData, file, indent=2, sort_keys=True)
				return redirect(url_for('.initialize'))

		return render_template('initialize.html', navurl=navURL, styles=styles, sectData=sectData)
	else:
		return render_template('initialize.html', navurl=navURL, styles=styles, sectData=sectData)

@app.route("/water-log", methods=['GET', 'POST'])
def waterLog():
	if request.method == 'POST':
		if 'clear' in request.form.keys():
			file = open('static/water-log.txt', 'w')
			file.close()

		return redirect(url_for('.waterLog'))
	else:
		navURL = getNavURL()
		styles = getStyles()

		waterLog = None
		with open('static/water-log.txt') as file:
			waterLog = file.readlines()

		return render_template('water-log.html', navurl=navURL, styles=styles, waterLog=waterLog)

def getNavURL():
	navURL = {'index': url_for('.index'),
		'init': url_for('.initialize'),
		'waterLog': url_for('.waterLog')
	}

	return navURL

def getStyles():
	styles = url_for('static', filename='styles.css')

	return styles

def getSectData():
	sectData = None

	with open('static/watering-sectors.json', 'r') as file:
		sectData = json.load(file)

	return sectData

if __name__ == '__main__':
	app.run(debug=True)
