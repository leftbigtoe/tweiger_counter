/**
 * Gets the WPM (words per minute) pushed every second
 * and displays the result using a servo.
 */

#include <Servo.h>
Servo servo;

// The pins
const int servoPin = 6;
const int speakerPin = 9;

// Variable for the alarm
boolean hadAlarm = false;


void setup()
{
  // Serial for receiving
  Serial.begin(9600);
  servo.attach(servoPin); 
  pinMode(speakerPin, OUTPUT);
  servo.write(3);
}

void loop()
{
  while(Serial.available() < 8);

  int wpm = Serial.read();
  if(wpm > 180) {
    tone(speakerPin, 1000, 20); 
  }
  // alarm for high wpms
  else if(!hadAlarm && wpm > 175){
    hadAlarm = true;
	// alarm sound
    for(int i = 0 ; i < 10 ; i++) {
      tone(speakerPin, 1000, 200);
      delay(100); 
      tone(speakerPin, 2000, 200); 
      delay(100);
    }
  }
  else{
    servo.write(wpm);
  }
}
