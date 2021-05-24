#from pyowm.owm import OWM
from datetime import date

#cary_lat = 35.791538
#cary_lon = -78.781120

#mgr = owm.weather_manager()

#log file to read forcast from
log = open("weather_log.txt", "r")
fcast = log.readlines()
fcastToday = ""

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
#	today = str(24)

	if foreDate == today:
		fcastToday += str(time) + ", " + str(status) + "\n"

	#print to test extraction
	#print("time: " + str(time) + ", status: " + str(status))
	#print("Today's date: " + str(today) + ", Forecast date: " + str(foreDate) + ", Forecast hour: " + str(foreHour))
print(str(fcastToday))

if fcastToday != '' and "rain" in fcastToday:
	print("water the plants, and perform other logical functions.")

log.close()
