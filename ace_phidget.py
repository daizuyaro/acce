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

    if len(ace) == 512:
        for i in range(512):
            x_dir.append(ace[i][0])
            x = x_dir

        for i in range(512):
            y_dir.append(ace[i][1])
            y = y_dir

        for i in range(512):
            z_dir.append(ace[i][2]) # offset gravity 1g
            z = z_dir

    elif len(ace) > 512:
        ace = []
        x_dir = []
        y_dir = []
        z_dir = []

def main(port):
    accelerometer0 = Accelerometer()
    accelerometer0.setHubPort(port)
    accelerometer0.setOnAccelerationChangeHandler(onAccelerationChange)
    accelerometer0.openWaitForAttachment(1000)
    accelerometer0.setDataInterval(10)
    time.sleep(5.5)
    accelerometer0.close()

    return x, y, z

#main()