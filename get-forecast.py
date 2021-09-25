from pyowm.owm import OWM

#api key
owm = OWM('1c29d386be313a4c1bc91710a3ff6d01')

#api call
mgr = owm.weather_manager()
fcast = mgr.forecast_at_place('Raleigh,US', '3h').forecast

#log file to save forcast to
log = open("forecast.txt", "w")

#write forecast from api call to log
for weather in fcast:
	log.write(str(weather) + "\n")

log.close()
