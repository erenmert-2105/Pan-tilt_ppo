const int dirPin1 = 2;
const int stepPin1 = 3;
const int dirPin2 = 4;
const int stepPin2 = 5;
const int ms1pin1 = 49;
const int ms2pin1 = 51;
const int ms3pin1 = 53;
const int ms1pin2 = 47;
const int ms2pin2 = 45;
const int ms3pin2 = 43;

int ms11 = 1;
int ms21 = 0;
int ms31 = 1;

int ms12 = 1;
int ms22 = 0;
int ms32 = 1;

int dir1 = 1;
int dir2 = 0;

float step1 = 1.0;
float step2 = 1.0;

int automode = 0;

int minimumdelay = 500;

void setup() {
  pinMode(dirPin1, OUTPUT);
  pinMode(dirPin2, OUTPUT);
  pinMode(stepPin1, OUTPUT);
  pinMode(stepPin2, OUTPUT);
  pinMode(ms1pin1, OUTPUT);
  pinMode(ms2pin1, OUTPUT);
  pinMode(ms3pin1, OUTPUT);
  pinMode(ms1pin2, OUTPUT);
  pinMode(ms2pin2, OUTPUT);
  pinMode(ms3pin2, OUTPUT);
  
  Serial.begin(115200);
}

void loop() {
  SerialCommunication(); // read serial
  Ridemotor();
  SendStatus();
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
      digitalWrite(dirPin2, HIGH);
    } else if (dir2 == -1) {
      digitalWrite(dirPin2, LOW);
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
    delayMicroseconds(minimumdelay + ((1 - step2) * 2500));
    digitalWrite(stepPin2, LOW);
    delayMicroseconds(minimumdelay + ((1 - step2) * 2500));
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
    delayMicroseconds(minimumdelay + ((1 - step1) * 2500));
    digitalWrite(stepPin1, LOW);
    delayMicroseconds(minimumdelay + ((1 - step1) * 2500));
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


void SendStatus() {
  Serial.print("ms11:");
  Serial.print(ms11);
  Serial.print(" ms21:");
  Serial.print(ms21);
  Serial.print(" ms31:");
  Serial.print(ms31);
  Serial.print(" dir1:");
  Serial.print(dir1);
  Serial.print(" step1:");
  Serial.print(step1);  

  // İkinci motor için değişkenlerin gönderilmesi
  Serial.print(" ms12:");
  Serial.print(ms12);
  Serial.print(" ms22:");
  Serial.print(ms22);
  Serial.print(" ms32:");
  Serial.print(ms32);
  Serial.print(" dir2:");
  Serial.print(dir2);
  Serial.print(" step2:");
  Serial.print(step2);
  
  Serial.print(" automode:");
  Serial.println(automode);
}
