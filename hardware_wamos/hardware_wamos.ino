
#include <SoftwareSerial.h>
// IMPORT ALL REQUIRED LIBRARIES

#include <math.h>

#ifndef ARDUINOJSON_H
#include <ArduinoJson.h>
#endif

//**********ENTER IP ADDRESS OF SERVER******************//

#define HOST_IP "172.16.193.147"  // REPLACE WITH IP ADDRESS OF SERVER ( IP ADDRESS OF COMPUTER THE BACKEND IS RUNNING ON)
#define HOST_PORT "8080"         // REPLACE WITH SERVER PORT (BACKEND FLASK API PORT)
#define route "api/update"       // LEAVE UNCHANGED
#define idNumber "620142646"     // REPLACE WITH YOUR ID NUMBER

// WIFI CREDENTIALS
#define SSID "MonaConnect"  // "REPLACE WITH YOUR WIFI's SSID"
#define password ""         // "REPLACE WITH YOUR WiFi's PASSWORD"

#define stay 100

//**********PIN DEFINITIONS******************//


#define espRX 10
#define espTX 11
#define espTimeout_ms 300
int trigPin = 4;  // Trigger
int echoPin = 3;  // Echo



/* Declare your functions below */
double waterheight(double in);
double reserves(double wh);
double percentage(double res);



SoftwareSerial esp(espRX, espTX);

double Waterheight, Reserves, Percentage;
long duration, inches;

void setup() {

  Serial.begin(115200);
  // Configure GPIO pins here
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);


  espInit();
}

void loop() {
  // The sensor is triggered by a HIGH pulse of 10 or more microseconds.
  // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the signal from the sensor: a HIGH pulse whose
  // duration is the time (in microseconds) from the sending
  // of the ping to the reception of its echo off of an object.
  pinMode(echoPin, INPUT);
  duration = pulseIn(echoPin, HIGH);

  // Convert the time into a distance
  inches = (duration / 2) / 74;  // Divide by 74 or multiply by 0.0135
  double WH = waterheight(inches);
  double RSRV = reserves(WH);
  double Percent = percentage(RSRV);


  // send updates with schema ‘{"id": "student_id", "type": "ultrasonic", "radar": 0, "waterheight": 0, "reserve": 0, "percentage": 0}’

  StaticJsonDocument<1000> doc;  // Create JSon object
  char message[290] = { 0 };

  // Add key:value pairs to JSon object
  doc["id"] = "620142646";
  doc["type"] = "ultrasonic";
  doc["radar"] = inches;
  doc["waterheight"] = WH;
  doc["reserve"] = RSRV ;
  doc["percentage"] = Percent;


  serializeJson(doc, message);  // Seralize / Covert JSon object to JSon string and store in char* array
  espUpdate(message);



  delay(1000);
}


void espSend(char command[]) {
  esp.print(command);  // send the read character to the esp
  while (esp.available()) { Serial.println(esp.readString()); }
}


void espUpdate(char mssg[]) {
  char espCommandString[50] = { 0 };
  char post[290] = { 0 };

  snprintf(espCommandString, sizeof(espCommandString), "AT+CIPSTART=\"TCP\",\"%s\",%s\r\n", HOST_IP, HOST_PORT);
  espSend(espCommandString);  //starts the connection to the server
  delay(stay);

  // GET REQUEST
  // snprintf(post,sizeof(post),"GET /%s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n",route,HOST_IP,strlen(mssg),mssg);

  // POST REQUEST
  snprintf(post, sizeof(post), "POST /%s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n", route, HOST_IP, strlen(mssg), mssg);

  snprintf(espCommandString, sizeof(espCommandString), "AT+CIPSEND=%d\r\n", strlen(post));
  espSend(espCommandString);  //sends post length
  delay(stay);
  Serial.println(post);
  espSend(post);  //sends POST request with the parameters
  delay(stay);
  espSend("AT+CIPCLOSE\r\n");  //closes server connection
}

void espInit() {
  char connection[100] = { 0 };
  esp.begin(115200);
  Serial.println("Initiallizing");
  esp.println("AT");
  delay(1000);
  esp.println("AT+CWMODE=1");
  delay(1000);
  while (esp.available()) { Serial.println(esp.readString()); }

  snprintf(connection, sizeof(connection), "AT+CWJAP=\"%s\",\"%s\"\r\n", SSID, password);
  esp.print(connection);

  delay(3000);  //gives ESP some time to get IP

  if (esp.available()) { Serial.print(esp.readString()); }

  Serial.println("\nFinish Initializing");
}

//***** Design and implement all util functions below ******


double waterheight(double in) {
  // CALCULATES WATERHEIGHT FROM RADAR MEASUREMENT
  double inches = in;
  if(inches > 94.5){
    inches = 94.5;
  }
  Waterheight = 94.5 - inches;
  return Waterheight;
}

double reserves(double wh) {
  Reserves = (wh / 77.763) * 1000;
  return Reserves;
}

double percentage(double res) {
  Percentage = res / 10;
  return Percentage;
}
