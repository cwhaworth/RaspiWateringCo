from pyowm.owm import OWM

#api key
owm = OWM('YOUR-API-KEY-HERE')

#api call
mgr = owm.weather_manager()
fcast = mgr.forecast_at_place('Raleigh,US', '3h').forecast

#log file to save forcast to
log = open("forecast.txt", "w")

#write forecast from api call to log
for weather in fcast:
	log.write("Forecast: " + str(weather) + "\n")

log.close()
