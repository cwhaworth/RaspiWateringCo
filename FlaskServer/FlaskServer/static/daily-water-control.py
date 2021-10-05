import json
from datetime import date
from datetime import datetime

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

	time = line[reftime : reftimeend]
	status = line[refstatus : refstatend]
	time = time.replace("reference_time=", "")
	status = status.replace("status=", "")

	#isolate system date, and forecast time
	foreDate = time[8 : 10]
	foreHour = time[11 : 13]
	today = str(date.today())
	today = today[8 : 10]
#	today = '04'

	if foreDate == today:
		fcastToday += str(time) + ", " + str(status) + "\n"

	#print to test extraction
	#print("time: " + str(time) + ", status: " + str(status))
	#print("Today's date: " + str(today) + ", Forecast date: " + str(foreDate) + ", Forecast hour: " + str(foreHour))

#perform, and log actions
log = open('/var/www/FlaskServer/static/water-log.txt', 'a')
sectData = None
with open('/var/www/FlaskServer/static/watering-sectors.json', 'r') as f:
	sectData = json.load(f)
now = datetime.now()

#if it rains: reset last-rained, and write to log
if fcastToday != '' and "rain" in fcastToday:
	log.write(now.strftime("%m/%d/%Y %H:%M:%S") + " Did not water, because it rained today.\n")
	sectData["last-rained"] = 0
	#print(fcastToday[ : 10] + " -> do not water the plants, and perform other logical functions.")
	with open('/var/www/FlaskServer/static/watering-sectors.json', 'w') as f:
		json.dump(sectData, f, indent=2, sort_keys=True)

#if it does not rain: water sectors based on interval
elif fcastToday != '':
	sectData["last-rained"] += 1
	line = now.strftime("%m/%d/%Y %H:%M:%S") + " Watered sector(s): "
	for sector in sectData["sector"]:
		if sector["rain-inc"] <= sectData["last-rained"] and sectData["last-rained"] % sector["rain-inc"] == 0:
			line += str(sector["id"]) + ", "
	line = line[ : -2]
	line += "\n"
	log.write(line)
	#print(fcastToday[ : 10] + " -> water the plants, and perform other logical functions.")
	with open('/var/www/FlaskServer/static/watering-sectors.json', 'w') as f:
		json.dump(sectData, f, indent=2, sort_keys=True)

#if get forecast operation returned erroneous
else:
	sectData["last-rained"] += 1
	#print(fcastToday[ : 10] + " -> forecast data was not initialized correctly. correct error in 'get-forecast.py'")
	with open('/var/www/FlaskServer/static/watering-sectors.json', 'w') as f:
		json.dump(sectData, f, indent=2, sort_keys=True)
	log.write(now.strftime("%m/%d/%Y %H:%M:%S") + " Forecast data was not initialized correctly. correct error in 'get-forecast.py'.\n")

log.close()
