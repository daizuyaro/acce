import test
import temp_phidget
import rpm_mcp3008
import csv
import datetime

file_path = "c://temp//a.csv"

all_data = []
all_data1 = []

coff_ace0 = 1
coff_ace1 = 1
coff_ace2 = 1
coff_ace3 = 1
coff_ace4 = 1
coff_ace5 = 1
coff_temp6 = 1
coff_temp7 = 1
coff_temp8 = 1
coff_temp9 = 1
coff_rpm0 = 1
coff_rpm1 = 1


ch0 = bytes([0x01,0x80,0x00])
ch1 = bytes([0x01,0x90,0x00])


# temperature phidget
for ch in range(4):
    if ch == 0:
        temp_ch0 = temp_phidget.temp_phidget(ch)
        temp_ch0 = [n * coff_temp6 for n in temp_ch0]
        all_data.append(temp_ch0)

    if ch == 1:
        temp_ch1 = temp_phidget.temp_phidget(ch)
        temp_ch1 = [n * coff_temp7 for n in temp_ch1]
        all_data.append(temp_ch1)

    if ch == 2:
        temp_ch2 = temp_phidget.temp_phidget(ch)
        temp_ch2 = [n * coff_temp8 for n in temp_ch2]
        all_data.append(temp_ch2)

    if ch == 3:
        temp_ch2 = temp_phidget.temp_phidget(ch)
        temp_ch2 = [n * coff_temp8 for n in temp_ch2]
        all_data.append(temp_ch2)

# rpm
ch = [ch0, ch1]
for ch in ch:

    if ch == ch0:
        rpm_ch0 = rpm_mcp3008.rpm_mcp3008(ch)
        rpm_ch0 = [n * coff_rpm0 for n in rpm_ch0]
        all_data.append(rpm_ch0)

    if ch == ch1:
        rpm_ch1 = rpm_mcp3008.rpm_mcp3008(ch)
        rpm_ch1 = [n * coff_rpm0 for n in rpm_ch1]
        all_data.append(rpm_ch1)

# acceleration phidget
for port in range(6):
    if port == 0:
        port0 = test.data(port)
        port0 = [n * coff_ace0 for n in port0]
        all_data.append(port0)

    if port == 1:
        port1 = test.data(port)
        port1 = [n * coff_ace1 for n in port1]
        all_data.append(port1)

    if port == 2:
        port2 = test.data(port)
        port0 = [n * coff_ace2 for n in port2]
        all_data.append(port2)

    if port == 3:
        port3 = test.data(port)
        port3 = [n * coff_ace3 for n in port3]
        all_data.append(port3)

    if port == 4:
        port4 = test.data(port)
        port4 = [n * coff_ace4 for n in port4]
        all_data.append(port4)

    if port == 5:
        port5 = test.data(port)
        port5 = [n * coff_ace5 for n in port5]
        all_data.append(port5)

#logger
if len(all_data) == len(all_data):
    for p in range(int(len(all_data))):
        q = all_data[p]
        for r in q:
            all_data1.append(r)

csvlist = all_data1
print(type(csvlist))

print(csvlist)
_csv.Error: iterable expected, not type


dt = datetime.datetime.now()
dt1 = dt.strftime('%Y/%m/%d')
dt2 = dt.strftime('%H:%M')
f = open(file_path, 'a')
writer = csv.writer(f, lineterminator='\n')
csvlist.append(dt) # date
csvlist.append(dt1) # time
csvlist.append(csvlist) # time
writer.writerow(list)
f.close()