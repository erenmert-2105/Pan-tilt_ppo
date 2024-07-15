import numpy as np
from collections import deque
import serial
import threading
import time
import tensorflow as tf
import random
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


"""
# 265 action space
# Actions
dir1 = np.array([-1, 0, 1])
step1 = np.round(np.arange(0, 1.1, 0.1), 1)  # 0.0, 0.1, 0.2, ..., 1.0
dir2 = np.array([-1, 0, 1])
step2 = np.round(np.arange(0, 1.1, 0.1), 1)  # 0.0, 0.1, 0.2, ..., 1.0

# Meshgrid oluştur
grid = np.meshgrid(dir1, step1, dir2, step2)

# Her bir olasılığı vektör haline getir
grid = [g.flatten() for g in grid]

# Kombinasyonları bir araya getir ve transpoze et
combinations = np.array(grid).T

# İlk değeri 0 olup 3. değeri 0 olmayan satırları bul
mask = ~((combinations[:, 0] == 0) & (combinations[:, 2] != 0))

# Maskeye göre satırları filtrele
combinations = combinations[mask]

indices_to_delete = np.where(((combinations[:, 0] == 0) & (combinations[:, 1] > 0)) | ((combinations[:, 2] == 0) & (combinations[:, 3] > 0))|(combinations[:, 0] != combinations[:, 2]) & (combinations[:, 2] != 0))


actions = np.delete(combinations, indices_to_delete, axis=0)
"""

""" # 9540 action space
dir1 = np.array([-1, 0, 1])
step1 = np.round(np.arange(0, 1.1, 0.1), 1)  # 0.0, 0.1, 0.2, ..., 1.0
dir2 = np.array([-1, 0, 1])
step2 = np.round(np.arange(0, 1.1, 0.1), 1)  # 0.0, 0.1, 0.2, ..., 1.0
motomod1 = np.array([1, 2, 4, 8,16,32])
motomod2 = np.array([1, 2, 4, 8,16,32])

# Meshgrid oluştur
grid = np.meshgrid(dir1, step1, dir2, step2, motomod1, motomod2)

# Her bir olasılığı vektör haline getir
grid = [g.flatten() for g in grid]

# Kombinasyonları bir araya getir ve transpoze et
combinations = np.array(grid).T

# İlk değeri 0 olup 3. değeri 0 olmayan satırları bul
mask = ~((combinations[:, 0] == 0) & (combinations[:, 2] != 0))

# Maskeye göre satırları filtrele
combinations = combinations[mask]

indices_to_delete = np.where(((combinations[:, 0] == 0) & (combinations[:, 1] > 0)) | ((combinations[:, 2] == 0) & (combinations[:, 3] > 0))|(combinations[:, 0] != combinations[:, 2]) & (combinations[:, 2] != 0))


actions = np.delete(combinations, indices_to_delete, axis=0)
"""



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
        
        self.olddir1 = self.dir1
        self.olddir2 = self.dir2        
        
        self.pan_target=0
        self.tilt_target=0
        
        self.pan_  = 500
        self.tilt_ = 500
        
        self.punishmant_factor = 0
        self.distancefactor = 1
        
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
        
    def updateDirections(self):
    
        # Initialize directions
        dir1 = 0
        dir2 = 0
        
        panError = self.shortest_rotation()
        if panError > self.tolerance/2:
            dir1 = 1  # Pan artır
            dir2 = 1
        elif panError < -self.tolerance/2:
            dir1 = -1  # Pan azalt
            dir2 = -1
        else:
            if self.state_system[1] <= self.tilt_target - self.tolerance/2:
                dir1 = 1  # Tilt artır
                dir2 = 0
            elif self.state_system[1] > self.tilt_target + self.tolerance/2:
                dir1 = -1  # Tilt azalt
                dir2 = 0

    
        return dir1, dir2

    
    def shortest_rotation(self):
        clockwise = (self.pan_target - self.state_system[0] + 360) % 360
        counter_clockwise = (self.state_system[0] - self.pan_target + 360) % 360
    
        if clockwise < counter_clockwise:
            return clockwise  # Pozitif yönde hareket
        else:
            return -counter_clockwise  # Negatif yönde hareket  
        
    def Done(self):
        while self.thread_flag2:
            fit_status = self.if_fit()
            
            if self.state_system[2] != 0:
                self.done_condition = 1
            elif fit_status < 0:
                self.done_condition = 0
            else:
                counter = 0
                while fit_status == 3 :
                    time.sleep(0.1)
                    fit_status = self.if_fit()
                    counter += 1
                    if counter >= 15: # 15sec
                        self.done_condition = 1
                        break
                    
                    
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
        if pan_diff <= self.tolerance/2 and tilt_diff <= self.tolerance/2:
            return 3
        if pan_diff <= self.tolerance and tilt_diff <= self.tolerance:
            return 2
        elif  pan_diff <= self.tolerance/2:
            return 1.5
        elif tilt_diff <= self.tolerance/2:
            return 1
        elif pan_diff >= self.tolerance and tilt_diff >= self.tolerance:
            return -2
        else:
            return -1
            

        
            
    def close(self):
        self.thread_flag = False
        self.thread_flag2 = False
        self.ser.close()      
        
    def Readdata(self):
      
        try:
            while self.thread_flag:
                line = self.ser.readline().decode('utf-8').strip()
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
        pan_diff = self.shortest_rotation()
        

        
        modes = {
            1: (0, 0, 0),
            2: (1, 0, 0),
            4: (0, 1, 0),
            8: (1, 1, 0),
            16: (0, 0, 1),
            32: (1, 0, 1)
        }
        if pan_diff <= self.tolerance/2 :
            if tilt_diff < 1:
                mode = 32
            elif tilt_diff < 5:
                mode = 16
            elif tilt_diff < 20:
                mode = 8
            elif tilt_diff < 30:
                mode = 4
            elif tilt_diff < 40:
                mode = 2
            else:
                mode = 1
        else:
            if pan_diff < 1:
                mode = 32
            elif pan_diff< 5:
                mode = 16
            elif pan_diff < 20:
                mode = 8
            elif pan_diff < 90:
                mode = 4
            elif pan_diff < 120:
                mode = 2
            else:
                mode = 1
    
        self.ms11, self.ms21, self.ms31 = modes[mode]
        self.ms12, self.ms22, self.ms32 = modes[mode]
        
        
        

    def Check_tilt(self):
        
        
        state=abs(self.tilt_target-self.state_system[1]) - abs(self.tilt_ - self.tilt_target)
        
        if state >2.5 :
            self.tilt_ = self.state_system[1]
            return -4
        
        elif state < 1.25:
            self.tilt_ = self.state_system[1]
            return 2
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
            return -4
        elif state < 1.25:
            self.pan_ = self.state_system[0]
            return 2

        else:
            self.pan_ = self.state_system[0]
            return 0
               
            
        
    def Reward(self):
        
        reward = 0 
        
        
        reward -=(( self.punishmant_factor/self.distancefactor ) * 10) # Time punishment
        fit_condision=self.if_fit()
              
        
        if fit_condision < 0:
            
            if self.dir1 == self.olddir1: #shaking
                reward += 75
            else:
                reward -= 100
                
        
        if fit_condision < 0:        
            reward += self.Check_pan()*50  # if getting closer tilt 
             
        if fit_condision == 1.5:
            reward += self.Check_tilt()*50     # if getting closer pan            
            
        
        if fit_condision == 3:  #tolarance/2 # if fit and motors break
            reward += 300
            if self.dir1 == 0 and self.dir2 == 0 :
                reward += 200
            else:
                reward -= 125
        elif fit_condision == 2: # tolarance 
            reward += 150

        
        # Check pitch error limits
        if self.state_system[2] == 1:
            reward += -500
        elif self.state_system[2]== 2:
            reward += -750
        elif self.state_system[2]== 3:
            reward += -1000
            
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
        
        panError = self.shortest_rotation()
        tiltError = abs(self.tilt_target - self.state_system[1])
        
        self.distancefactor = panError + tiltError
        
        self.Senddata()
        print("system off oto pilot mod ")    
        
        return self.state_system[0],self.state_system[1],self.Reward(),int(self.done_condition),self.state_system[2]
               
    def State(self):
        return self.state_system[0],self.state_system[1],self.pan_target,self.tilt_target,self.Reward(),int(self.done_condition),self.state_system[2]



    def Run(self,action,i):

        self.olddir1=self.dir1
        self.olddir2=self.dir2
        self.dir1            = action[0]
        self.step1           = action[1]
        self.dir2            = action[2]
        self.step2           = action[3]
        self.punishmant_factor = i

        
        self.Motomoder()

        self.Senddata()    
        
        return self.state_system[0],self.state_system[1],self.pan_target,self.tilt_target,self.Reward(),int(self.done_condition),self.state_system[2]

class ActorCritic:
    def __init__(self, action_size):
        self.action_size = action_size

        
        # Actor model
        self.actor = Sequential()
        self.actor.add(Dense(action_size, input_dim=5, activation='relu')) # state
        self.actor.add(Dense(132, activation='relu'))
        self.actor.add(Dense(162, activation='relu'))
        self.actor.add(Dense(242, activation='relu'))
        self.actor.add(Dense(action_size, activation='softmax'))  # action
        self.actor.compile(optimizer='adam', loss=self.policy_gradient_loss)
        
        # Critic model
        self.critic = Sequential()
        self.critic.add(Dense(242, input_dim=5, activation='relu'))  # state action
        self.critic.add(Dense(132, activation='relu'))
        self.critic.add(Dense(162, activation='relu'))
        self.critic.add(Dense(242, activation='relu'))
        self.critic.add(Dense(1, activation='linear'))  # Output layer: Q-value
        self.critic.compile(optimizer='adam', loss='mean_squared_error')

    def policy_gradient_loss(self, y_true, y_pred):
        advantages = y_true[:, :-1]
        actions = y_true[:, -1]
        actions = tf.cast(actions, tf.int32)
        
        action_prob = tf.reduce_sum(y_pred * tf.one_hot(actions, self.action_size), axis=1)
        log_prob = tf.math.log(action_prob + 1e-10)
        loss = -tf.reduce_sum(log_prob * advantages)    
        
        return loss
    
 
    

class Main:
    def __init__(self):
        self.env = Env()  
        self.actions = self.Actions()
        self.agent = ActorCritic(len(self.actions))
        self.done = 0
        #self.random_factor = 100000
        #self.random_factor = 20000
        self.random_factor = 15000
        self.memory = deque(maxlen=3000)


    def Actions(self):
        dir1 = np.array([-1, 0, 1])
        step1 = np.round(np.arange(0, 1.1, 0.1), 1)  # 0.0, 0.1, 0.2, ..., 1.0
        dir2 = np.array([-1, 0, 1])
        step2 = np.round(np.arange(0, 1.1, 0.1), 1)  # 0.0, 0.1, 0.2, ..., 1.0

        # Create meshgrid
        grid = np.meshgrid(dir1, step1, dir2, step2)

        # Flatten each possibility vector
        grid = [g.flatten() for g in grid]

        # Combine and transpose the combinations
        combinations = np.array(grid).T

        # Find rows where the first value is 0 and the third value is not 0
        mask = ~((combinations[:, 0] == 0) & (combinations[:, 2] != 0))

        # Filter rows according to the mask
        combinations = combinations[mask]

        indices_to_delete = np.where(
            ((combinations[:, 0] == 0) & (combinations[:, 1] > 0)) | 
            ((combinations[:, 2] == 0) & (combinations[:, 3] > 0)) |
            ((combinations[:, 0] != combinations[:, 2]) & (combinations[:, 2] != 0))
        )

        actions = np.delete(combinations, indices_to_delete, axis=0)
        
        return actions
    
    def Targetcaller(self):
        target = np.array([np.random.randint(0, 361), np.random.randint(-70, 71) ]) # target[0] = pan, target[1] = tilt
        return target

    def Start(self): 
        duration = 15
        print("System collecting data")
        target = self.Targetcaller()
        self.env.AutoPilotOff(target)
        pan_, tilt_, pan_target_, tilt_target_, reward_, self.done, error_ = self.env.State() 
        time.sleep(1)
        
        counter = 0
       
        for i in range(2000): #4500 * 20 ms = 1.5 minutes
            if self.done > 0:
                break
            
            start_time = time.time()
            
            if self.random_factor > 0 and counter == 0 :
                counter = 1
                time.sleep(0.02)
                self.random_factor -= 1
                random_sample = self.actions[np.random.choice(self.actions.shape[0])]                   
                random_sample[0],random_sample[2]=self.env.updateDirections()
                actor_value = np.where((self.actions == random_sample).all(axis=1))[0][0]
                selected_action = self.actions[actor_value]
            elif self.random_factor >0 and counter == 1 :
                counter = 0
                time.sleep(0.02)
                self.random_factor -= 1
                if random.random() >= 0.3:
                    random_sample = self.actions[np.random.choice(self.actions.shape[0])]
                    random_sample[0],random_sample[2]=self.env.updateDirections()
                    actor_value = np.where((self.actions == random_sample).all(axis=1))[0][0]
                    selected_action = self.actions[actor_value]
                else:
                    random_sample = self.actions[np.random.choice(self.actions.shape[0])]
                    actor_value = np.where((self.actions == random_sample).all(axis=1))[0][0]
                    selected_action = self.actions[actor_value]
            else:
                if random.random() > 0.2 :
                    
                    actor_out = self.agent.actor.predict(np.array([[pan_, tilt_, pan_target_, tilt_target_,duration]])) 
                    actor_value = np.argmax(actor_out)
                    selected_action = self.actions[actor_value]
                else:
                    random_sample = self.actions[np.random.choice(self.actions.shape[0])]
                    actor_value = np.where((self.actions == random_sample).all(axis=1))[0][0]
                    selected_action = self.actions[actor_value]
            
            

            pan, tilt, pan_target, tilt_target, reward, self.done, error = self.env.Run(selected_action,i)
            #print(pan, tilt,self.done, error)
            end_time = time.time()
            duration = int((end_time - start_time)*1000)
            
            self.memory.append([pan_, tilt, pan_target_, tilt_target_,duration,actor_value, pan, tilt, pan_target, tilt_target, reward, self.done])
            
            pan_, tilt_, pan_target_, tilt_target_ = pan, tilt, pan_target, tilt_target
        
        self.env.AutoPilotOn() #system automaticly fix it self to 0,0
        self.Learning()
            
    def Learning(self):
        gamma = 0.7  # Discount factor
        print("system learning")
        total_steps = len(self.memory)
        
        # Initialize numpy arrays for losses
        actor_losses = np.array([])
        critic_losses = np.array([])
        rewards = np.array([])

        for i, state in enumerate(self.memory):
            pan_, tilt_, pan_target_, tilt_target_, duration, actor_value, pan, tilt, pan_target, tilt_target, reward, done = state
            
            rewards = np.append(rewards, state[10])
            
            state_current = np.array([pan_, tilt_, pan_target_, tilt_target_, duration]).reshape(1, -1)
            state_next = np.array([pan, tilt, pan_target, tilt_target, duration]).reshape(1, -1)
            
            # Compute the critic value for the current and next state
            value_current = self.agent.critic.predict(state_current)
            value_next = self.agent.critic.predict(state_next)
            
            # Compute the target value
            target = reward + gamma * value_next * (1 - done)
            
            # Train the critic and store the loss
            critic_history = self.agent.critic.fit(state_current, target, verbose=0)
            critic_loss = critic_history.history['loss'][0]
            critic_losses = np.append(critic_losses, critic_loss)
            
            # Compute the advantage
            advantage = target - value_current
            
            if self.random_factor <= 0:
                # Train the actor and store the loss
                y_true = np.zeros((1, self.agent.action_size + 1))
                y_true[0, :-1] = advantage
                y_true[0, -1] = np.argmax(actor_value)
                actor_history = self.agent.actor.fit(state_current, y_true, verbose=0)
                actor_loss = actor_history.history['loss'][0]
                actor_losses = np.append(actor_losses, actor_loss)
            
            # Print remaining steps
            remaining_steps = total_steps - (i + 1)
            print(f"Step {i + 1}/{total_steps} completed. {remaining_steps} steps remaining.")

        if self.random_factor <= 0:
            # Append losses to text files
            with open("actor_loss.txt", "a") as actor_file:
                np.savetxt(actor_file, actor_losses, fmt='%f')
                
        with open("critic_loss.txt", "a") as critic_file:
            np.savetxt(critic_file, critic_losses, fmt='%f')
            
        with open("rewards.txt", "a") as rewards_file:
            np.savetxt(rewards_file, rewards, fmt='%f')
        
        # Clear memory
        self.memory.clear()


            
    def Loop(self):
        counter =0
        
        while True:      #connections
            
            if self.env.state_system[0] is None:
                
                
                print("waiting for connection !")
                time.sleep(10)
            else:
                if counter ==0:
                    counter = 1
                    print("connection succesfull !")
                    break
                
        while True: #main loop
        
            if self.env.state_system[2] <= 0 and self.env.state_system[2] !=None : # error check
                self.Start()
            elif self.env.state_system[2] == None: 
                print("No cencor data")
                time.sleep(5)
            elif self.env.state_system[2] == 3:                
                print("system need manual fix tilt")
                time.sleep(5)
            else:
                print("wating system to fix tilt")
                time.sleep(5)



def delete_files_if_exist():
    # file names
    files_to_check = ['actor_loss.txt', 'critic_loss.txt', 'rewards.txt']
    
    for file in files_to_check:
        # check if exist
        if os.path.exists(file):
            # delete if exist
            os.remove(file)            
        else:
            pass




                        

delete_files_if_exist()      

# Create an instance of the Main class
main = Main()

main.Loop()




