'/*****************************************************************
 * Automatic door automation
 * Testing Wiring:
 *  Board: Arduino UNO (Parallel)
 *  Fingerprint <--> Arduino
 *  White cable <--> 3
 *  Green cable <--> 2
 *  Black cable <--> GND 
 *  Red cabble <--> 5V 
 * 
 * 
 * Relay <--> Arduino
 * In <--> 4
 * Based on: 
 *  https://www.geekering.com/?p=241
 *  https://learn.adafruit.com/adafruit-optical-fingerprint-sensor/downloads
 *  
 * LCD Library: https://bitbucket.org/fmalpartida/new-liquidcrystal/downloads/NewliquidCrystal_1.3.4.zip
 ******************************************************************/
#include <Adafruit_Fingerprint.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define RELAY_PIN 4
#define ON LOW
#define OFF HIGH

SoftwareSerial mySerial(2,3);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);
LiquidCrystal_I2C lcd(0x27,2,1,0,4,5,6,7,3, POSITIVE);

void setup() {  
  pinMode(RELAY_PIN,OUTPUT);
  digitalWrite(RELAY_PIN,OFF);
  
  lcd.begin (16,2);
  lcd.setBacklight(HIGH);
  lcd.setCursor(0,0);
  lcd.print("Arte do Andre =D");
  lcd.setCursor(0,1);

  
  // set the data rate for the sensor serial port
  finger.begin(57600);
  delay(5);
  //finger.verifyPassword() ? Serial.println("Found fingerprint sensor!") : Serial.println("Did not find fingerprint sensor :(");
  finger.verifyPassword() ? lcd.print("Found fingerprint sensor!") : lcd.print("Did not find fingerprint sensor");
  delay(1000);
  ClearLine(1,16,2,lcd);

  finger.getTemplateCount();

  if (finger.templateCount == 0) {
    lcd.print("Sensor doesn't contain any fingerprint data. Please run the 'enroll' example.");
  } 
  else {
    lcd.print(finger.templateCount); lcd.print(" templates");
  }
  
  delay(1000);
  ClearLine(1,16,2,lcd);

  lcd.print("Poe o dedinho ai");
  
}

void loop() {
  int getFingerResponse = getFingerprintID();
  Serial.print("Achei algo "); Serial.println(getFingerResponse);
    
  if(getFingerResponse > 0){
    ClearLine(1,16,2,lcd);
    lcd.print("Ola ");
    lcd.print(getName(finger.fingerID));
    digitalWrite(RELAY_PIN,ON);
    delay(5000);
    digitalWrite(RELAY_PIN,OFF);
    ClearLine(1,16,2,lcd);
    lcd.print("Poe o dedinho ai");
  }
  else if(getFingerResponse == -2){
    ClearLine(1,16,2,lcd);
    lcd.print("Quem eh vc?");
    delay(2000);
    ClearLine(1,16,2,lcd);
    lcd.print("Poe o dedinho ai");
  }
  else{
    delay(500); 
  }
}
