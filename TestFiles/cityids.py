#testing file, does not currently work
from pyowm.commons import cityids
from pyowm.commons import cityidregistry

raleigh = cityidregistry.ids_for('raleigh', country='US', matching='nocase')
print(str(raleigh))
