#include <basicMPU6050.h>

basicMPU6050<> imu;

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
  imu.setup();
  imu.setBias();
  Serial.begin(115200);
}

void loop() {
  float startTime = millis();

  imu.updateBias();
  
  acceleration.x = imu.ax();
  acceleration.z = imu.gz();

  Serial.print("tilt: ");
  Serial.print(acceleration.x);
  Serial.print(" ");
  
  float endTime = millis();
  rotation.time = endTime - startTime;

  dummyaw();

  Serial.print("pan: ");
  Serial.print(rotation.yaw);
  Serial.print("    ");
  
  Serial.print("Loop Duration: ");
  Serial.print(rotation.time);
  Serial.println(" ms");
}

void dummyaw() {
  rotation.yaw = rotation.yaw + (acceleration.z * 9.81 * (rotation.time / 1000.0));
}
