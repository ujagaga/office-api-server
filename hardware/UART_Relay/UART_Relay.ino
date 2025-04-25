const int RELEY1_PIN = 3;
const int RELEY2_PIN = 4;
const int BTN1_PIN = 5;
const int BTN2_PIN = 6;

volatile byte buffer[0xff];
uint8_t rdId = 0;
uint8_t wrId = 0;
uint8_t relay_state[2] = {0};

uint8_t rxCount(){
  return wrId - rdId;
} 

bool bufferFull(){
  return rxCount() > 3;
}

bool cmdIsSet(){
  return buffer[rdId] == 's';
}

void processBtnPress(){
  int btn1Press1 = digitalRead(BTN1_PIN);
  int btn2Press1 = digitalRead(BTN2_PIN);

  delay(20);

  int btn1Press2 = digitalRead(BTN1_PIN);
  int btn2Press2 = digitalRead(BTN2_PIN);

  if(btn1Press1 == btn1Press2 == LOW){
    if(relay_state[0] == 0){
      digitalWrite(RELEY1_PIN, 1); 
      relay_state[0] == 1;
    }else{
      digitalWrite(RELEY1_PIN, 0); 
      relay_state[0] == 0;
    } 

    while(digitalRead(BTN1_PIN) == 0){
      delay(20);
    }
  }

  if(btn1Press1 == btn1Press2 == LOW){
    if(relay_state[1] == 0){
      digitalWrite(RELEY2_PIN, 1); 
      relay_state[1] == 1;
    }else{
      digitalWrite(RELEY2_PIN, 0); 
      relay_state[1] == 0;
    } 

    while(digitalRead(BTN2_PIN) == 0){
      delay(20);
    }
  }
}

void setup() {
  Serial.begin(9600); 

  pinMode(RELEY1_PIN, OUTPUT);
  pinMode(RELEY2_PIN, OUTPUT);

  pinMode(BTN1_PIN, INPUT_PULLUP);
  pinMode(BTN2_PIN, INPUT_PULLUP);

  digitalWrite(RELEY1_PIN, LOW);
  digitalWrite(RELEY2_PIN, LOW);
}

void loop() {
  if (Serial.available() > 0){
    byte rx = Serial.read();

    if(rxCount() == 0){
      if((rx == 's') || (rx == 'g')){
        buffer[wrId] = rx;
        wrId++;
      }
    }else if(rxCount() == 1){
      if(rx == ':'){
        buffer[wrId] = rx;
        wrId++;
      }
    }else if(rxCount() < 4){
      buffer[wrId] = rx;
      wrId++;
    }    
  }

  if(bufferFull()){   
     
    if(cmdIsSet()){
      uint8_t out_state = 1;
      if(buffer[rdId+3] == '0'){
        out_state = 0;
      }

      if(buffer[rdId+2] == '0'){
        digitalWrite(RELEY1_PIN, out_state); 
        relay_state[0] = out_state;
      }else if(buffer[rdId+2] == '1'){
        digitalWrite(RELEY2_PIN, out_state); 
        relay_state[1] = out_state;
      }
    }

    rdId = wrId;

    Serial.write("s:");
    Serial.write('0' + relay_state[0]);
    Serial.write('0' + relay_state[1]);
    Serial.write("\n");
  }

}