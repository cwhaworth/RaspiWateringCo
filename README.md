# RaspiWateringCo
Using a Raspberry Pi 4 B as a solar powered watering system.

System components:
1. Raspberry Pi 4B; obtained
2. Raspberry Pi 4B compatible UPS; obtained
3. Raspberry Pi 4B compatible solar panel assembly; pending
4. Water pump, and bucket; obtained
5. Hoses; partially obtained
6. On/off controller for water pump; obtained, pending upgrade
7. Water flow control components; pending
8. Electronics container; pending
9. Short ciruit protection; ?, need more research

Data flow:
1. 'get-forecast.py' retreives 3-hour/5-day forecast, saves all to to 'forecast.txt'
2. 'daily-water-control.py' takes the next day forecast, and determines if it will water any sectors
-> 'daily-water-control.py' gets the logic for which sectors it waters from 'watering-sectors.json'
-> 'watering-sectors.json' keeps count of how many days have passed since the last rain as well as the day incriment for each sector
-> new sectors can be added to 'watering-sectors.json' by editing the file
3. 'daily-water-control.py' modifies 'watering-sectors.json' to update/reset the days since the last rain

File install instructions:
1. Determine where you want your log and JSON files then edit 'get-forecast.py', and 'daily-water-control.py' file paths accordingly 
-> also edit the JSON file to reflect which GPIO pin is in use for each sector
2. enter command 'crontab -e', and add the following entries:
0 23 * * * python3 ~/path/to/get-forcast.py
0 7 * * * python3 ~/path/to/daily-water-control.py
the entries will have 'get-forecast.py' run daily at 11pm, and 'daily-water-control.py' daily the next morning
