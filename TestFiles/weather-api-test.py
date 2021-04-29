from pyowm.owm import OWM
from pyowm.utils.config import get_config_from


#config_dict = get_config_from('weather-api-config.json')
owm = OWM('1c29d386be313a4c1bc91710a3ff6d01')

mgr = owm.weather_manager()
check = mgr.weather_at_place('Raleigh')
weather = check.weather
print("Weather now: " + str(weather))
