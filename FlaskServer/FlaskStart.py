from flask import Flask, jsonify, render_template, request, url_for
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
	data['weather'] = open('static/forecast.txt')
	#data['sectData'] = sectData
	#data['weather'] = weather
	print(data)
	return render_template('index.html', posts=jsonify(data))

@app.route("/initialize", methods=['POST'])
def initialize():
	return render_template('initialize.html')

@app.route("/water-log", methods=['POST'])
def waterLog():
	return render_template('water-log.html')

if __name__ == '__main__':
	app.run(debug=True)
