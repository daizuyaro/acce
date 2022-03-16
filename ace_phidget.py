from Phidget22.Phidget import *
from Phidget22.Devices.Accelerometer import *
import time

ace = []
x_dir = []
y_dir = []
z_dir = []

def onAccelerationChange(self, acceleration, timestamp):
    global ace, x_dir, y_dir, z_dir, x, y, z

    ace.append(acceleration)
    if len(ace) == 128:
        for i in range(128):
            x_dir.append(ace[i][0])
            x = x_dir
        for i in range(128):
            y_dir.append(ace[i][1])
            y = y_dir
        for i in range(128):
            z_dir.append(ace[i][2]) # offset gravity 1g
            z = z_dir


    elif len(ace) > 128:
        ace = []
        x_dir = []
        y_dir = []
        z_dir = []

def main():
    accelerometer0 = Accelerometer()
    accelerometer0.setOnAccelerationChangeHandler(onAccelerationChange)
    accelerometer0.openWaitForAttachment(1000)
    accelerometer0.setDataInterval(10)
    time.sleep(1.3)
    accelerometer0.close()

    return x, y, z

#main()