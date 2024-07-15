#include <basicMPU6050.h>
#include <TimerOne.h>
#include <TimerThree.h>

basicMPU6050<> imu;

const int dirPin1 = 2; // motor1
const int stepPin1 = 3;
const int ms1pin1 = 49;
const int ms2pin1 = 51;
const int ms3pin1 = 53;
const int enablePin1 = 41;

int ms11 = 0;
int ms21 = 1;
int ms31 = 0;

int dir1 = 0;
float step1 = 0;


const int dirPin2 = 4; // motor2
const int stepPin2 = 5;
const int ms1pin2 = 43;
const int ms2pin2 = 45;
const int ms3pin2 = 47;
const int enablePin2 = 39;

int ms12 = 1;
int ms22 = 0;
int ms32 = 1;

int dir2 = 0;
float step2 = 0.0;

int automode = 0;

float pan_target = 0;
float tilt_target = 0;
float tolerance = 1;

int resetmod = 0;
int pitch_error = 0;

const unsigned int minimumdelay = 6000;
const unsigned int delay_pool = 14000;
unsigned long interval1 = 0;
unsigned long interval2 = 0;

volatile bool toggle1 = false;
volatile bool toggle2 = false;

int control_moto1 = 0; 
int control_moto2 = 0; 



float pitch_estimate = 0.0; // Pitch tahmini
float pitch_error_estimate = 1.0; // Pitch hata tahmini
const float q = 0.001; // Process noise covariance
const float r = 0.03; // Measurement noise covariance
const float alpha = 0.5; // Düşük geçişli filtreleme faktörü

int counter = 0;


int x_index = 0;
int z_index = 0;

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

void sensor_data() {
  
  acceleration.x_g = imu.ax();
  acceleration.z = imu.gz();
  
  
  dumyaw();
  dumpitch();
}



// Functions starts here

void motostateOn() {
  digitalWrite(enablePin1,LOW);
  digitalWrite(enablePin2,LOW);
}

void motostateOff() {
  digitalWrite(enablePin1,HIGH);
  digitalWrite(enablePin2,HIGH);
}


void updateDirections() {
    // Önce tilt sonra pan kontrol et
    if (!isTiltInTarget()) {
      if (rotation.pitch < tilt_target ) {
        dir1 = 1; // Tilt artır
        dir2 = 0;
      } else if (rotation.pitch > tilt_target) {
        dir1 = -1; // Tilt azalt
        dir2 = 0;
      }
    } else if (!isPanInTarget()) {
      float panError = shortest_rotation(rotation.yaw, pan_target);
      if (panError > tolerance) {
        dir1 = 1; // Pan artır
        dir2 = 1;
      } else if (panError < -tolerance) {
        dir1 = -1; // Pan azalt
        dir2 = -1;
      }
    } else {
      dir1 = 0;
      dir2 = 0;
      
    }
  }




bool isTiltInTarget() {
  if ((rotation.pitch < tilt_target + tolerance) && (rotation.pitch > tilt_target - tolerance)){
    return true;
  }
  else {
    return false;
  }
}


bool isPanInTarget() {
  float panError = shortest_rotation(rotation.yaw, pan_target);
  return (abs(panError) <= tolerance || abs(panError - 360) <= tolerance);
}


float shortest_rotation(float current_angle, float target_angle) {
  float clockwise = fmod(target_angle - current_angle + 360, 360);
  float counter_clockwise = fmod(current_angle - target_angle + 360, 360);

  if (clockwise < counter_clockwise) {
    return clockwise; // Pozitif yönde hareket
  } else {
    return -counter_clockwise; // Negatif yönde hareket
  }
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
  interval1 = (minimumdelay + ((1.0 - step1) * delay_pool));
  interval2 = (minimumdelay + ((1.0 - step2) * delay_pool));

  interval1 = max(interval1, minimumdelay);
  interval2 = max(interval2, minimumdelay);

  // Timer'ları yeni interval ile yeniden başlatın
  Timer1.setPeriod(interval1);
  Timer3.setPeriod(interval2);
}

void dumyaw() {
  // Eski yaw değerini sakla
  double oldYaw = rotation.yaw;

  // Yaw hesaplamasını yap
  double newYaw = rotation.yaw + (acceleration.z * 9.81 * 8 * (rotation.time / 1000.0));

  // Yaw değeri 0-360 aralığında kalmasını sağla
  if (newYaw < 0) {
    newYaw += 360;
  }

  if (newYaw > 360) {
    newYaw -= 360;
  }
  
  // High pass
  if (fabs(newYaw - oldYaw) > 0.01) {
    rotation.yaw = newYaw;
  }
}



void dumpitch() {
  // Eski pitch değerini sakla
  float old_pitch = rotation.pitch;

  // Yeni pitch değerini hesapla
  float new_pitch;
  
  if (acceleration.x_g < 0) {
    new_pitch = acceleration.x_g * 0.95 * 100;
  } else {
    new_pitch = acceleration.x_g * 0.85 * 100;
  }

  // Kalman filtresi uygulaması
  // 1. Prediction update
  pitch_error_estimate = pitch_error_estimate + q;

  // 2. Measurement update
  float kalman_gain = pitch_error_estimate / (pitch_error_estimate + r);
  pitch_estimate = pitch_estimate + kalman_gain * (new_pitch - pitch_estimate);
  pitch_error_estimate = (1 - kalman_gain) * pitch_error_estimate;

  // Düşük geçişli filtre uygulaması
  float updated_pitch = alpha * pitch_estimate + (1 - alpha) * rotation.pitch;

  // Değişim miktarını hesapla
  float pitch_change = fabs(updated_pitch - old_pitch);


  if (pitch_change < 0.08) {
    return;
  }


  if (pitch_change > 2.5) {
    if (updated_pitch > old_pitch) {
      rotation.pitch = old_pitch + 1.5;
    } else {
      rotation.pitch = old_pitch - 1.5;
    }
  } else {
    // Değişimi olduğu gibi uygula
    rotation.pitch = updated_pitch;
  }
}





void Ridemotor() {
  if ((dir1 != dir2) && (dir1 != 0) && (dir2 != 0)) {
    dir1=0;
    dir2=0;
}
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
    }
    digitalWrite(stepPin1, LOW);
  } else {
    if (control_moto1 == 1) {
      control_moto1 = 0;
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
    for (int i = 1; i <= 10; i++) {
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
          case 10:
            automode = atof(token);
            break;
        }
      }
    }
  }
}

void SendStatus_test() { // pan tilt error pitch_error time 

  Serial.print(ms11);
  Serial.print(" ");

  Serial.print(ms21);
  Serial.print(" ");

  Serial.print(ms31);
  Serial.print(" ");

  Serial.print(dir1);
  Serial.print(" ");

  Serial.print(step1);
  Serial.print(" ");

  Serial.print(ms12);
  Serial.print(" ");

  Serial.print(ms22);
  Serial.print(" ");

  Serial.print(ms32);
  Serial.print(" ");

  Serial.print(dir2);
  Serial.print(" ");

  Serial.print(step2);
  Serial.print(" ");

  Serial.println(automode);
}

void SendStatus() { // pan tilt error pitch_error time 
  
  Serial.print(rotation.yaw);
  Serial.print(" ");

  Serial.print(rotation.pitch);
  Serial.print(" ");

  Serial.print(pitch_error);
  Serial.print(" ");

  Serial.println(rotation.time);

   
}



void error_check() {
    if ((rotation.pitch >= -2.5 && rotation.pitch <= 2.5) && pitch_error > 0) {
        if (enablePin1 == HIGH){
            motostateOn();
        }
        pitch_error = 0;
        dir1 = 0;
        dir2 = 0;
    }

    if (rotation.pitch < -88 || rotation.pitch > 88) {
        pitch_error = 3;
        motostateOff();
    } 
    else if (rotation.pitch < -85 || rotation.pitch > 85) {
        if (pitch_error != 3) {
            pitch_error = 2;
        }
    } 
    else if (rotation.pitch < -80 || rotation.pitch > 80) {
        if (pitch_error != 3) {
            pitch_error = 1;
        }
    }
}



void setup() {
  pinMode(dirPin1, OUTPUT); // motor 1
  pinMode(stepPin1, OUTPUT);
  pinMode(ms1pin1, OUTPUT);
  pinMode(ms2pin1, OUTPUT);
  pinMode(ms3pin1, OUTPUT);
  pinMode(enablePin1, OUTPUT);

  pinMode(dirPin2, OUTPUT); // motor 2
  pinMode(stepPin2, OUTPUT);
  pinMode(ms1pin2, OUTPUT);
  pinMode(ms2pin2, OUTPUT);
  pinMode(ms3pin2, OUTPUT);
  pinMode(enablePin2, OUTPUT);

  rotation.yaw = 0;

  imu.setup();
  imu.setBias();

  Serial.begin(115200);

  // TimerOne ayarları
  Timer1.initialize(50000000); // Başlangıç için 500000 mikro saniye (500ms)
  Timer1.attachInterrupt(timerISR1); // Kesme fonksiyonunu bağlama

  // TimerThree ayarları
  Timer3.initialize(50000000); // Başlangıç için 500000 mikro saniye (500ms)
  Timer3.attachInterrupt(timerISR2); // Kesme fonksiyonunu bağlama

  motostateOn();
}




void loop() {
  float startTime = millis(); 
  imu.updateBias();

  sensor_data();

  
  
  error_check();
  SerialCommunication();
  
  if ( (pitch_error > 0 && pitch_error < 3 ) || automode == 1 ){
    
    ms11 = 1;
    ms21 = 1;
    ms31 = 0;

    ms12 = 1;
    ms22 = 1;
    ms32 = 0;

    step1 = 1;
    step2 = 1;

    pan_target = 0;
    tilt_target = 0;

    updateDirections();  

    Ridemotor();
  }

  else if ( (pitch_error == 0 ) ) {

    
    Ridemotor(); 
  } 



  float endTime = millis();
  rotation.time = endTime - startTime;

  
  SendStatus();
}
