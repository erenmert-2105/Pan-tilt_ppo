#include <basicMPU6050.h>
#include <TimerOne.h>
#include <TimerThree.h>

basicMPU6050<> imu;

const int dirPin1 = 2; // motor1
const int stepPin1 = 3;
const int ms1pin1 = 49;
const int ms2pin1 = 51;
const int ms3pin1 = 53;

int ms11 = 1;
int ms21 = 0;
int ms31 = 1;

int dir1 = 1;
float step1 = 0.0;

const int dirPin2 = 4; // motor2
const int stepPin2 = 5;
const int ms1pin2 = 43;
const int ms2pin2 = 45;
const int ms3pin2 = 47;

int ms12 = 1;
int ms22 = 0;
int ms32 = 1;

int dir2 = 1;
float step2 = 0.0;

const unsigned int minimumdelay = 500;
unsigned long interval1 = 0;
unsigned long interval2 = 0;

volatile bool toggle1 = false;
volatile bool toggle2 = false;

int control_moto1 = 0; 
int control_moto2 = 0; 

struct Acceleration {
  float x_g; 
  float z;   
};

struct Rotation {
  float yaw;   
  float pitch; 
  float time;  
};

Acceleration acceleration;
Rotation rotation;




void setup() {
  pinMode(dirPin1, OUTPUT); // motor 1
  pinMode(stepPin1, OUTPUT);
  pinMode(ms1pin1, OUTPUT);
  pinMode(ms2pin1, OUTPUT);
  pinMode(ms3pin1, OUTPUT);

  pinMode(dirPin2, OUTPUT); // motor 2
  pinMode(stepPin2, OUTPUT);
  pinMode(ms1pin2, OUTPUT);
  pinMode(ms2pin2, OUTPUT);
  pinMode(ms3pin2, OUTPUT);

  rotation.yaw = 0;

  imu.setup();
  imu.setBias();

  Serial.begin(115200);

  // TimerOne ayarları
  Timer1.initialize(500000); // Başlangıç için 500000 mikro saniye (500ms)
  Timer1.attachInterrupt(timerISR1); // Kesme fonksiyonunu bağlama

  // TimerThree ayarları
  Timer3.initialize(500000); // Başlangıç için 500000 mikro saniye (5ms)
  Timer3.attachInterrupt(timerISR2); // Kesme fonksiyonunu bağlama
}

void loop() {
  float startTime = millis(); // imu part
  imu.updateBias();
  acceleration.x_g = imu.ax();
  acceleration.z = imu.gz();

  SerialCommunication(); // Motor control part
  
  Ridemotor();
  

  float endTime = millis();
  rotation.time = endTime - startTime;

  dumyaw();
  dumpitch();
  
  SendStatus();
  //SendStatusdeemo();
}



void timerISR1() {
  if (control_moto1 == 0){ 
    toggle1 = !toggle1;
    digitalWrite(stepPin1, toggle1);
  }
}

void timerISR2() {
  if (control_moto2 == 0){ 
    toggle2 = !toggle2;
    digitalWrite(stepPin2, toggle2);
  }
}
void updateTimerIntervals() {
  interval1 = (minimumdelay + ((1.0 - step1) * 2500));
  interval2 = (minimumdelay + ((1.0 - step2) * 2500));

  interval1 = max(interval1, minimumdelay);
  interval2 = max(interval2, minimumdelay);

  // Timer'ları yeni interval ile yeniden başlatın
  Timer1.setPeriod(interval1);
  Timer3.setPeriod(interval2);
}

void dumyaw() {
  // Yaw hesaplamasını yap
  rotation.yaw = rotation.yaw + (acceleration.z * 9.81 * 8 * (rotation.time / 1000.0));
  
  if (rotation.yaw < 0) {
    rotation.yaw += 360;
  }

  if (rotation.yaw > 360) {
    rotation.yaw -= 360;
  }
}

void dumpitch() {
  if (acceleration.x_g < 0) {
    rotation.pitch = acceleration.x_g * 0.95 * 100;
  }

  if (acceleration.x_g > 0) {
    rotation.pitch = acceleration.x_g * 0.85 * 100;
  }
}

void Ridemotor() {
  // Motor 2
  if (dir2 == 0) {
    if (control_moto2 == 0) {
      control_moto2 = 1;
    }
    digitalWrite(stepPin2, LOW);
  } else {
    if (control_moto2 == 1) {
      control_moto2 = 0;
    }

    digitalWrite(dirPin2, dir2 == 1 ? HIGH : LOW);
    digitalWrite(ms1pin2, ms12 == 1 ? HIGH : LOW);
    digitalWrite(ms2pin2, ms22 == 1 ? HIGH : LOW);
    digitalWrite(ms3pin2, ms32 == 1 ? HIGH : LOW);
    
  }

  // Motor 1
  if (dir1 == 0) {
    if (control_moto1 == 0) {
      control_moto1 = 1;
      Serial.println("Motor 1 stopped");
    }
    digitalWrite(stepPin1, LOW);
  } else {
    if (control_moto1 == 1) {
      control_moto1 = 0;
      Serial.println("Motor 1 started");
    }

    digitalWrite(dirPin1, dir1 == 1 ? HIGH : LOW);
    digitalWrite(ms1pin1, ms11 == 1 ? HIGH : LOW);
    digitalWrite(ms2pin1, ms21 == 1 ? HIGH : LOW);
    digitalWrite(ms3pin1, ms31 == 1 ? HIGH : LOW);
    
  }

  updateTimerIntervals();
}


void SerialCommunication() {
  if (Serial.available() > 0) {
    // Okunan veriyi bir string değişkenine atıyoruz
    String data = Serial.readStringUntil('\n');

    // String'i parçalayabilmek için bir yardımcı değişken kullanıyoruz
    char* charArray = const_cast<char*>(data.c_str());

    // strtok fonksiyonunu kullanarak boşluklara göre veriyi parçalıyoruz
    char* token = strtok(charArray, " ");

    // İlk değeri ms11'e atıyoruz
    ms11 = atoi(token);

    // Diğer değerleri sırasıyla okuyup ilgili değişkenlere atıyoruz
    for (int i = 1; i <= 9; i++) {
      token = strtok(NULL, " ");
      if (token != NULL) {
        switch (i) {
          case 1:
            ms21 = atoi(token);
            break;
          case 2:
            ms31 = atoi(token);
            break;
          case 3:
            dir1 = atoi(token);
            break;
          case 4:
            step1 = atof(token);
            break;
          case 5:
            ms12 = atoi(token);
            break;
          case 6:
            ms22 = atoi(token);
            break;
          case 7:
            ms32 = atoi(token);
            break;
          case 8:
            dir2 = atoi(token);
            break;
          case 9:
            step2 = atof(token);
            break;
        }
      }
    }
  }
}

void SendStatusdeemo() { // pan tilt loopduration ms11 ms21 ms31 dir1 step1 ms12 ms22 ms32 dir2 step2
  
  Serial.print(rotation.yaw);
  Serial.print(" ");

  Serial.print(rotation.pitch);
  Serial.print(" ");
  

  Serial.print(interval1);
  Serial.print(" ");

  Serial.println(interval2);
  Serial.print(" ");

}
void SendStatus() { // pan tilt loopduration ms11 ms21 ms31 dir1 step1 ms12 ms22 ms32 dir2 step2
  
  Serial.print(rotation.yaw);
  Serial.print(" ");

  Serial.print(rotation.pitch);
  Serial.print(" ");
  
  Serial.print(rotation.time);
  
  Serial.print(" ");
  
  Serial.print(ms11);
  Serial.print(" ");
  
  Serial.print(ms21);
  Serial.print(" ");

  Serial.print(ms31);
  Serial.print(" ");
  
  Serial.print(dir1);
  Serial.print(" ");

  Serial.print(step1, 2);  
  Serial.print(" ");
  
  Serial.print(ms12);
  Serial.print(" ");
  
  Serial.print(ms22);
  Serial.print(" ");

  Serial.print(ms32);
  Serial.print(" ");

  Serial.print(dir2);
  Serial.print(" ");

  Serial.println(step2, 2);  

}
