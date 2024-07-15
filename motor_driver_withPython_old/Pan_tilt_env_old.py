import numpy as np
import serial
import threading
import time
import random


"""
dir1 + dir2 - pan decrising
dir - dir2 + pan incrising


dir1 + dir2 - tilt incrising
dir1 - dir2 + tilt decrising

pan range 0 to 360
tilt -85 to + 85

"""

class Env:
    
    def __init__(self):
        self.ser = serial.Serial("COM6", 115200)
        self.state_system = np.array([None,None,None,None,None,None,None,None,None,None,None,None,None])
        #for state_system pan,tilt,duration,ms11,ms21,ms31,dir1,step1,ms12,ms22,ms32,dir2,step2
        

        
        self.target=np.array([10,10])
        self.tilt_dis = 0
        self.pan_dis = 0
        self.tol=5
        
        self.motomoder_param_tilt = 90
        self.motomoder_param_pan  = 180
        
        self.ms11 = 1
        self.ms21 = 0
        self.ms31 = 1
        self.dir1 = 0
        self.step1 = 1.0

        
        self.ms12 = 1
        self.ms22 = 0
        self.ms32 = 1
        self.dir2 = 0
        self.step2 = 1.0
        
        self.thread_flag = True
        self.thread_flag_timer = False
        
        self.timer_done= False
        
        thread = threading.Thread(target=self.Readdata)
        thread.start()        
        
                
    def close(self):
        self.thread_flag = False
        self.thread_flag_timer = False
        self.ser.close()
         
        
    def Timer(self):
        start_time = time.time()
        while time.time() - start_time < 30:
            if not self.thread_flag_timer:
                break
            time.sleep(0.01)  # 10 ms bekle
        self.timer_done = True        
        
    def Readdata(self):
  
        try:
            while True:
                if self.thread_flag:
                    line = self.ser.readline().decode().strip()
                    values = line.split()
                    if len(values) == 13:
                        self.state_system  [0] = float(values[0]) # pan 
                        self.state_system  [1] = float(values[1]) # tilt
                        self.state_system  [2] = float(values[2]) # loop_duration
                        self.state_system  [3] = float(values[3]) # ms12
                        self.state_system  [4] = float(values[4]) # ms22
                        self.state_system  [5] = float(values[5]) # ms32
                        self.state_system  [6] = float(values[6]) # dir2
                        self.state_system  [7] = float(values[7]) # step2
                        self.state_system  [8] = float(values[8]) # ms11
                        self.state_system  [9] = float(values[9]) # ms21
                        self.state_system  [10] = float(values[10]) # ms31
                        self.state_system  [11] = float(values[11]) # dir1
                        self.state_system  [12] = float(values[12]) # step1
                        
                else:
                    break
        except KeyboardInterrupt:
            pass
            
    def close(self):
        self.thread_flag = False
        self.ser.close()
        self.thread.join()            
            
    def Senddata(self):
        time.sleep(0.005)

        data_to_send = f"{self.ms11} {self.ms21} {self.ms31} {self.dir1} {self.step1} {self.ms12} {self.ms22} {self.ms32} {self.dir2} {self.step2}\n"
        self.ser.write(data_to_send.encode())
            
            
    def Cal_distance(self):
        self.distance= self.tilt_dis + self.pan_dis
    
    def Motomoder(self): # Bak buna
        

        
        if self.motomoder_param  > self.distance:
            
            self.ms11=0
            self.ms21=0
            self.ms31=0
            
            self.ms12=0
            self.ms22=0
            self.ms32=0
            
        elif self.motomoder_param /32  < self.distance :
            self.ms11=1
            self.ms21=0
            self.ms31=1
            
            self.ms12=1
            self.ms22=0
            self.ms32=1
            
        elif self.motomoder_param /16  < self.distance :
            self.ms11=0
            self.ms21=0
            self.ms31=1
            
            self.ms12=0
            self.ms22=0
            self.ms32=1
            
        elif self.motomoder_param /8  < self.distance :
            self.ms11=0
            self.ms21=0
            self.ms31=1
            
            self.ms12=0
            self.ms22=0
            self.ms32=1
            
        elif self.motomoder_param /4  < self.distance :
            self.ms11=1
            self.ms21=1
            self.ms31=0
            
            self.ms12=1
            self.ms22=1
            self.ms32=0
            
        elif self.motomoder_param /2  < self.distance :
            self.ms11=1
            self.ms21=0
            self.ms31=0
            
            self.ms12=1
            self.ms22=0
            self.ms32=0
            
        
        
    def New_Target(self): # Bak buna
        
        tilt_now= self.state_system  [1]
        pan_now= self.state_system  [0]
        
        tilt_target=self.target[0]
        pan_target =self.target[1]
        
        tilt_tolarance = abs(tilt_target-tilt_now)
        pan_tolarance = abs(pan_target-pan_now)
        
        if self.thread_flag_timer == True and  tilt_tolarance > self.tol and  pan_tolarance > self.tol:
            print("Someting went wrong ! trying to fit !")
            self.thread_flag_timer = False
        
        if self.timer_done == True and tilt_tolarance <= self.tol and  pan_tolarance <= self.tol:
            print("Success ! going new target")
            self.thread_flag_timer = False
            
        elif tilt_tolarance <= self.tol and  pan_tolarance <= self.tol:
            print("oN target ! wating 30 seconds")
            self.thread_flag_timer = True
            thread = threading.Thread(target=self.Timer())
            thread.start()        
    def Direction_Caller_demo(self):
                self.dir1 =  -1 
                self.dir2 =   1
    def Direction_Caller(self):
        
        tilt_now= self.state_system  [1]
        pan_now= self.state_system  [0]
        
        tilt_target=self.target[0]
        pan_target =self.target[1]
        

        
        # fix pan for 0 360 range
        if not tilt_now > 87 or tilt_now < -87:
            
            
            if tilt_now + self.tol < tilt_target:
                self.dir1 =   0 
                self.dir2 =   1
                
            elif tilt_now - self.tol > tilt_target:
                self.dir1 =   0
                self.dir2 =  -1 
                

            elif pan_now + self.tol  < pan_target :
                self.dir1 = -1
                self.dir2 =  1
               
            elif pan_now + self.tol  > pan_target:
                self.dir1 = 1
                self.dir2 = -1
          
            else:
                self.dir1 = 0
                self.dir2 = 0         
        else:   
            self.step2=0
            self.step1=0
            print(" error : motors are on break ! tilt on limits ! tilt angle is : ") + str(tilt_now)
            self.close()
            



            

    def close(self):
        # Motor kapatma işlemleri
        pass

            
            
                              
        
        
    def Run(self,step1,step2):

        self.step1=step1
        self.step2=step2
        
        #self.Cal_distance
        #self.Motomoder()
        
        #self.Direction_Caller() 
        self.Direction_Caller_demo()
        

        #self.New_Target()
        self.Senddata()

        




pantilt_controller = Env()  

counter=0
while True:      
    
    while pantilt_controller.state_system[0] is None:
        
        
        print("waiting for connection !")
        time.sleep(10)
    if counter ==0:
        counter = 1 
        print("connection succesfull !")
        
    if pantilt_controller.state_system[0] != None:
        
       start_time = time.time() 
       
       pantilt_controller.Run(0.5,0.5)
       print(pantilt_controller.state_system)
       
       end_time = time.time()
       elapsed_time = end_time - start_time
       print(f"Geçen süre: {elapsed_time} saniye")

  


# current positon
# current angles
# target postion
# previous action
#
# reward


            
            
            
    
    
    

    
    

    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    