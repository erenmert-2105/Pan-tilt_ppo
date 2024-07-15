const int dirPin1 = 2;
const int stepPin1 = 3;
const int ms1pin1 = 49;
const int ms2pin1 = 51;
const int ms3pin1 = 53;
int ms11 = 0;
int ms21 = 0;
int ms31 = 0;
int dir1 = 1;
float step1 = 0.1;
int maximumdelay = 2500;

void setup() {
  pinMode(dirPin1, OUTPUT);
  pinMode(stepPin1, OUTPUT);
  pinMode(ms1pin1, OUTPUT);
  pinMode(ms2pin1, OUTPUT);
  pinMode(ms3pin1, OUTPUT);
  
  Serial.begin(115200);
}

void loop() {
  SerialCommunication(); // Fonksiyonun argümanlarını kaldırın
  Ridemotor();
  SendStatus();
}

void Ridemotor() {
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
    for (int i = 1; i <= 2; i++) {
      token = strtok(NULL, " ");
      if (token != NULL) {
        switch (i) {
          case 1:
            ms21 = atoi(token);
            break;
          case 2:
            ms31 = atoi(token);
            break;
        }
      }
    }

    token = strtok(NULL, " ");
    if (token != NULL) {
      dir1 = atoi(token);
    }

    token = strtok(NULL, " ");
    if (token != NULL) {
      step1 = atof(token);
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
  Serial.println(step1, 2);  // Ondalık kısmı iki basamakla sınırla
}
