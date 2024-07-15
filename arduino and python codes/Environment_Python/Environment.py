import numpy as np
import serial
import threading
import time
import random


class Env:
    
    def __init__(self):
        
        
        self.ser = serial.Serial("COM6", 115200)
        self.state_system = np.array([None,None,None,None])  # pan tilt error time 
        
        
        self.ms11 = 1 
        self.ms21 = 0
        self.ms31 = 1
        self.dir1 = 0
        self.step1 = 0
        
        self.ms12 = 1
        self.ms22 = 0
        self.ms32 = 1
        self.dir2 = 0
        self.step2 = 0
        
        
        self.pan_target=0
        self.tilt_target=0
        
        self.pan_  = 500
        self.tilt_ = 500
        
        self.automode = 0
        
        self.done_condition=0    
                      
        self.tolerance = 2.5
                       
        self.target = np.array([0, 0])
        
        self.thread_flag = True
        self.thread_flag2 = True
        
        self.thread = threading.Thread(target=self.Readdata)
        self.thread.start() 
        
        self.thread2 = threading.Thread(target=self.Done)
        self.thread2.start() 
        
    def Done(self):
        while self.thread_flag2:
            fit_status = self.if_fit()
            
            if self.state_system[2] != 0:
                self.done_condition = 1
            elif fit_status < 0:
                self.done_condition = 0
            else:
                counter = 0
                while fit_status > 0 and counter <= 100:
                    time.sleep(0.1)
                    fit_status = self.if_fit()
                    counter += 1
                if counter >= 100:
                    self.done_condition = 1
                    
                    
            time.sleep(0.01)  # Tek bir bekleme süresi ile döngüyü kontrol ediyoruz

   
        
    def if_fit(self):
        if self.state_system[1]  == None :
            return 0
        # Tilt close ?
        tilt_diff = abs(self.tilt_target - self.state_system[1])
        
        # Pan close ?
        pan_diff = min(abs(self.pan_target - self.state_system[0]), 
                       360 - abs(self.pan_target - self.state_system[0]))
        
        
        
        # Success ?
        if pan_diff <= self.tolerance and tilt_diff <= self.tolerance:
            return 3
        elif pan_diff >= self.tolerance and tilt_diff >= self.tolerance:
            return -2
        else:
            return -1
            

        
            
    def close(self):
        self.thread_flag = False
        self.thread_flag2 = False
        self.ser.close()      
        
    def Readdata(self):
        time.sleep(0.001)
      
        try:
            while self.thread_flag:
                line = self.ser.readline().decode().strip()
                values = line.split()
                if len(values) == 4:
                    
                    self.state_system[0] = float(values[0])  # pan 
                    self.state_system[1] = float(values[1])  # tilt
                    self.state_system[2] = float(values[2])  # error
                    self.state_system[3] = float(values[3])  # time 
        except Exception as e:
            print(f"Error reading data: {e}")  
            
     
    def Senddata(self): # ms11 ms21 ms31 dir1 step1 ms12 ms22 ms32 dir2 step2
        time.sleep(0.005)
        data_to_send = f"{self.ms11} {self.ms21} {self.ms31} {self.dir1} {self.step1} {self.ms12} {self.ms22} {self.ms32} {self.dir2} {self.step2} {self.automode}\n"
        try:
            self.ser.write(data_to_send.encode())
        except Exception as e:
            print(f"Error sending data: {e}")

        
    def Motomoder(self):
        
        tilt_diff = abs(self.tilt_target - self.state_system[1])
        
        modes = {
            1: (0, 0, 0),
            2: (1, 0, 0),
            4: (0, 1, 0),
            8: (1, 1, 0),
            16: (0, 0, 1),
            32: (1, 0, 1)
        }
    
        if tilt_diff < 5:
            mode = 32
        elif tilt_diff < 10:
            mode = 16
        elif tilt_diff < 20:
            mode = 8
        elif tilt_diff < 40:
            mode = 4
        elif tilt_diff < 60:
            mode = 2
        else:
            mode = 1
    
        self.ms11, self.ms21, self.ms31 = modes[mode]
        self.ms12, self.ms22, self.ms32 = modes[mode]
        

    def Check_tilt(self):
        
        
        state=abs(self.tilt_target-self.state_system[1]) - abs(self.tilt_ - self.tilt_target)
        
        if state >2.5 :
            self.tilt_ = self.state_system[1]
            return -2
        
        elif state < 1.25:
            self.tilt_ = self.state_system[1]
            return 1
        else:
            self.tilt_ = self.state_system[1]
            return 0


    def Check_pan(self):
        # Açı farkını hesapla ve mod 360 ile sar
        pan_diff = (self.pan_target - self.state_system[0]) % 360
        if pan_diff > 180:
            pan_diff -= 360  # Negatif yönde daha kısa mesafe
    
        prev_diff = (self.pan_target - self.pan_) % 360
        if prev_diff > 180:
            prev_diff -= 360  # Negatif yönde daha kısa mesafe
    
        state = abs(pan_diff) - abs(prev_diff)
    
        if state > 2.5:
            self.pan_ = self.state_system[0]
            return -2
        elif state < 1.25:
            self.pan_ = self.state_system[0]
            return 1

        else:
            self.pan_ = self.state_system[0]
            return 0
               
            
        
    def Reward(self):
        
        reward = 0 
        
        
        reward -= 1  # Time punishment
              
        
        reward += self.if_fit() # Check if tilt and pan -2 +3
            
        reward += self.Check_tilt() # Check direction -2 1
        
        reward += self.Check_pan() # Check direction  -2 1
        
        # Check pitch error limits
        if self.state_system[2] == 1:
            reward -= 10
        elif self.state_system[2]== 2:
            reward -= 15
        elif self.state_system[2]== 3:
            reward -= 20
            
        return reward   
        
    
    def AutoPilotOn(self):

        self.automode = 1
        self.Senddata()
        self.tilt_target     = 0
        self.pan_target      = 0
        print("system on oto pilot mod ")
        
    def AutoPilotOff(self,target):
        
        self.automode = 0
        self.tilt_target     = target[1]
        self.pan_target      = target[0]
        
        self.Senddata()
        print("system off oto pilot mod ")    
        
        return self.state_system[0],self.state_system[1],self.Reward(),int(self.done_condition),self.state_system[2]
        
      
            
    def Run(self,dir1,step1,dir2,step2):
        
        
        self.dir1            = dir1
        self.step1           = step1
        self.dir2            = dir2
        self.step2           = step2

        
        self.Motomoder()

        self.Senddata()    
        
        return self.state_system[0],self.state_system[1],self.Reward(),int(self.done_condition),self.state_system[2]
    

        
dir1=0 #moto1 direction
step1=0 #moto1 speed
dir2=0 #motor2 direction
step2=0 #moto2 step



def Targetcaller():
    target = np.array([np.random.randint(0, 361), np.random.randint(-78, 79) ]) #target[0] = pan, target[1] = tilt
    return target



        
        
        
env = Env()   
     
       


counter =0

while True:      
    
    if env.state_system[0] is None:
        
        
        print("waiting for connection !")
        time.sleep(10)
    else:
        if counter ==0:
            counter = 1
            print("connection succesfull !")
            break
                
while True:
    
    # if bachzise fine go training else go more sample (BACKWARD OPERATİON)    
    
  
    if env.state_system[2] <= 0: # error check
        env.AutoPilotOff(Targetcaller())
        while True:      
                time.sleep(0.01)
            
                start_time = time.time()
                #(FORWARD OPERATİON)
                
                pan,tilt,reward,done,error=env.Run(dir1,step1,dir2,step2)  #interaction
                
            
                end_time = time.time()
                duration = int((end_time - start_time)*1000)
                
                print(f"Pan: {pan}, Tilt: {tilt}, Reward: {reward}, Done: {done}, Error: {error}, Duration: {duration} ms")
                
                #DATA COLLECTİON
                
                if done == 1:
                    env.AutoPilotOn()
                    break
    elif env.state_system[2] == 3: 
        print("system need manual fix tilt")
        time.sleep(5)
    else:
        print("wating system to fix tilt")
        time.sleep(5)
    
    




        

        
        
        
        
        
        
        