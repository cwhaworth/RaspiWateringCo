import json, time
from datetime import date, datetime
from gpiozero import CPUTemperature

cpu = CPUTemperature()
now = datetime.now()
sysData = None
with open('/var/www/FlaskServer/static/system-data.json', 'r') as f:
	sysData = json.load(f)
temperature = {
	'date': f'{now.strftime("%m/%d/%Y")}',
	'time': f'{now.strftime("%H:%M:%S")}',
	'temp': f'{round(cpu.temperature, 1)} C'
}
sysData['sysTemp'].append(temperature)

while len(sysData['sysTemp']) > 12:
	del sysData['sysTemp'][0]

with open('/var/www/FlaskServer/static/system-data.json', 'w') as f:
	json.dump(sysData, f, indent=2, sort_keys=True)
