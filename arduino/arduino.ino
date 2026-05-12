const int PIN_R = 8;
const int PIN_Y = 9;
const int PIN_G = 10;

void setup() {
  pinMode(PIN_R, OUTPUT);
  pinMode(PIN_Y, OUTPUT);
  pinMode(PIN_G, OUTPUT);
  
  Serial.begin(9600);
  setTL("");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim(); 
    setTL(input);
  }
}

void setTL(String c) {
  digitalWrite(PIN_R, c == "RED");
  digitalWrite(PIN_Y, c == "YELLOW");
  digitalWrite(PIN_G, c == "GREEN");
}
