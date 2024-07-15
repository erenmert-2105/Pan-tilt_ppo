import serial
import time
import numpy as np

data=np.array([])

# Arduino'nun bağlı olduğu seri portu belirtin (COMx)
ser = serial.Serial('COM6', 115200)  # COMx'i Arduino'nun bağlı olduğu port ile değiştirin

for i in range(2000):
    line = ser.readline().decode('utf-8').strip()
    print(line)
    data = np.append(data, line)
ser.close()



