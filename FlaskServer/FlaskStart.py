from flask import Flask, render_template, request, redirect, url_for
import json
app = Flask(__name__)

@app.route("/")
@app.route("/index", methods=['POST'])
def index():
	data = {'sectData': None,
		'weather': None
	}
	#sectData = None
	with open('static/watering-sectors.json') as f:
		data['sectData'] = json.load(f)
	forecast_file = open('static/forecast.txt')
	data['weather'] = getForecast(forecast_file) 

	styles = url_for('static', filename='styles.css')
	indexURL = redirect(url_for('index'))
	initURL = redirect(url_for('initialize'))
	waterLogURL = redirect(url_for('waterLog'))

	return render_template('index.html', data=data, styles=styles, indexurl=indexURL, initurl=initURL, waterurl=waterLogURL)

def getForecast(forecast_file):
	fcast = forecast_file.readlines()
	counter = 0
	weather = []

	for line in fcast:
		counter += 1

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
			time = extractTime[12 : ]

			data = {'date': date,
				'time': time,
				'status': status
			}
			weather.append(data)
	return weather

@app.route("/initialize", methods=['POST'])
def initialize():
	return render_template('initialize.html')

@app.route("/water-log", methods=['POST'])
def waterLog():
	return render_template('water-log.html')



if __name__ == '__main__':
	app.run(debug=True)
