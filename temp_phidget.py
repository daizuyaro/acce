from Phidget22.Phidget import *
from Phidget22.Devices.TemperatureSensor import *



def temp_phidget(ch):
    temperatureSensor = TemperatureSensor()
    temperatureSensor.setChannel(ch)
    temperatureSensor.openWaitForAttachment(1000)
    temperature = temperatureSensor.getTemperature()
    #print("Temperature: " + str(temperature))
    temperature = str(temperature)
    temperatureSensor.close()
    temperature = temperature[0:4]
    return [float(temperature)]