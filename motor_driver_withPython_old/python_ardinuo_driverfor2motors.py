import serial
import threading
import numpy as np
import time

state_system = np.array([None,None,None,None,None,None,None,None,None,None,None,None,None])# values stores here
thread_flag=True
start_time = time.time()
# Seri bağlantıyı oluştur
ser = serial.Serial("COM6", 115200)
end_time = time.time()
elapsed_time = f"{(end_time - start_time):.3f}"

print("Bağlantı başarılı ! Geçen süre ::", elapsed_time, "saniye")



def close():
    global ser
    global thread_flag
    ser.close()
    thread_flag= False

def Readdata():
    global ser
    global state_system 
    global thread_flag
    try:
        while True:
            if thread_flag:
                line = ser.readline().decode().strip()
                values = line.split()
                state_system [0] = float(values[0]) # pan 
                state_system [1] = float(values[1]) # tilt
                state_system [2] = float(values[2]) # loop_duration
                state_system [3] = float(values[3]) # ms11
                state_system [4] = float(values[4]) # ms21
                state_system [5] = float(values[5]) # ms31
                state_system [6] = float(values[6]) # dir1
                state_system [7] = float(values[7]) # step1
                state_system [8] = float(values[8]) # ms12
                state_system [9] = float(values[9]) # ms22
                state_system [10] = float(values[10]) # ms32
                state_system [11] = float(values[11]) # dir2
                state_system [12] = float(values[12]) # step2
            else:
                break
    except KeyboardInterrupt:
        print("cannot read data !")


def Senddata(ms11,ms21,ms31,dir1,step1,ms12,ms22,ms32,dir2,step2):
    global ser
    data_to_send = f"{ms11} {ms21} {ms31} {dir1} {step1} {ms12} {ms22} {ms32} {dir2} {step2}\n"
    ser.write(data_to_send.encode())


# İş parçacığını başlat
thread = threading.Thread(target=Readdata)
thread.start()

