#include <basicMPU6050.h>
basicMPU6050<> imu;

const int dirPin1 = 2; // moto1
const int stepPin1 = 3;
const int ms1pin1 = 49;
const int ms2pin1 = 51;
const int ms3pin1 = 53;

int ms11 = 0;
int ms21 = 0;
int ms31 = 0;
int dir1 = 1;
float step1 = 0.0;

const int dirPin2 = 4; // moto2
const int stepPin2 = 5;
const int ms1pin2 = 47;
const int ms2pin2 = 45;
const int ms3pin2 = 43;

int ms12 = 0;
int ms22 = 0;
int ms32 = 0;
int dir2 = 1;
float step2 = 0.0;



int maximumdelay = 2500;

struct Acceleration {
  float x;
  float z;
};

struct Rotation {
  float yaw;
  float time;
};

Acceleration acceleration;
Rotation rotation;

void setup() {
  pinMode(dirPin1, OUTPUT); // moto 1
  pinMode(stepPin1, OUTPUT);
  pinMode(ms1pin1, OUTPUT);
  pinMode(ms2pin1, OUTPUT);
  pinMode(ms3pin1, OUTPUT);

  pinMode(dirPin2, OUTPUT); // moto 2
  pinMode(stepPin2, OUTPUT);
  pinMode(ms1pin2, OUTPUT);
  pinMode(ms2pin2, OUTPUT);
  pinMode(ms3pin2, OUTPUT);
  
  imu.setup();
  imu.setBias();
  
  Serial.begin(115200);
}

void loop() {
  
  float startTime = millis(); // imu part
  imu.updateBias();  
  acceleration.x = imu.ax();
  acceleration.z = imu.gz();
  
  SerialCommunication(); // Moto control part
  Ridemotor();
  
  float endTime = millis();
  rotation.time = endTime - startTime;

  dummyaw();
  
  SendStatus();

}

void dummyaw() {
  rotation.yaw = rotation.yaw + (acceleration.z * 9.81 * (rotation.time / 1000.0));
}

void Ridemotor() {
//motor2
    if (dir2 == 0) {
    digitalWrite(dirPin2, HIGH);
    digitalWrite(ms1pin2, HIGH);
    digitalWrite(ms2pin2, HIGH);
    digitalWrite(ms3pin2, HIGH);
    digitalWrite(stepPin2, HIGH);
    }else {
    if (dir2 == 1) {
      digitalWrite(dirPin1, HIGH);
    } else if (dir2 == -1) {
      digitalWrite(dirPin1, LOW);
    }

    if (ms12 == 1) {
      digitalWrite(ms1pin2, HIGH);
    } else if (ms11 == 0) {
      digitalWrite(ms1pin2, LOW);
    }

    if (ms22 == 1) {
      digitalWrite(ms2pin2, HIGH);
    } else if (ms22 == 0) {
      digitalWrite(ms2pin2, LOW);
    }

    if (ms32 == 1) {
      digitalWrite(ms3pin2, HIGH);
    } else if (ms32 == 0) {
      digitalWrite(ms3pin2, LOW);
    }

    digitalWrite(stepPin2, HIGH);
    delayMicroseconds(500 + (maximumdelay * step2));
    digitalWrite(stepPin2, LOW);
    delayMicroseconds(500 + (maximumdelay * step2));
  }
// motor1    
  if (dir1 == 0) {
    digitalWrite(dirPin1, HIGH);
    digitalWrite(ms1pin1, HIGH);
    digitalWrite(ms2pin1, HIGH);
    digitalWrite(ms3pin1, HIGH);
    digitalWrite(stepPin1, HIGH);
  } else {
    if (dir1 == 1) {
      digitalWrite(dirPin1, HIGH);
    } else if (dir1 == -1) {
      digitalWrite(dirPin1, LOW);
    }

    if (ms11 == 1) {
      digitalWrite(ms1pin1, HIGH);
    } else if (ms11 == 0) {
      digitalWrite(ms1pin1, LOW);
    }

    if (ms21 == 1) {
      digitalWrite(ms2pin1, HIGH);
    } else if (ms21 == 0) {
      digitalWrite(ms2pin1, LOW);
    }

    if (ms31 == 1) {
      digitalWrite(ms3pin1, HIGH);
    } else if (ms31 == 0) {
      digitalWrite(ms3pin1, LOW);
    }

    digitalWrite(stepPin1, HIGH);
    delayMicroseconds(500 + (maximumdelay * step1));
    digitalWrite(stepPin1, LOW);
    delayMicroseconds(500 + (maximumdelay * step1));
  }
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

void SendStatus() { // pan tilt loopduration ms11 ms21 ms31 dir1 step1 ms12 ms22 ms32 dir2 step2
  
  Serial.print(rotation.yaw);
  Serial.print(" ");

  Serial.print(acceleration.x);
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
  
  Serial.print(ms11);
  Serial.print(" ");
  
  Serial.print(ms21);
  Serial.print(" ");

  Serial.print(ms31);
  Serial.print(" ");

  Serial.print(dir1);
  Serial.print(" ");

  Serial.println(step1, 2);  

}
