//Code developed by: Andre Botelho (02/2017)
//Part of Home Automation project 
//github.com/aobotelho2
//Based on: ItKindaWorks - Creative Commons 2016
#include <PubSubClient.h>
#include <ESP8266WiFi.h>


#define MQTT_SERVER_IP "192.168.1.30"
#define SOCKET1_PIN 2
#define SOCKET2_PIN 0
#define TOPIC_CATEGORY  "testingSocket"
#define TOPIC_CONFIRMATION  "confirmation"
#define SOCKET1_TOPIC "socket1"
#define SOCKET2_TOPIC "socket2"

//Defining Wireless SSID and password
const char* ssid = "Sumidouro de Baixo";
const char* password = "abc123def4";

//Define output pins
const int socket1Pin = SOCKET1_PIN;
const int socket2Pin = SOCKET2_PIN;

char* socket1Topic = "/testingSocket/socket1";
char* socket2Topic = "/testingSocket/socket2";

//Declaring callback function. Implementation is further ahead in the code
void callback(char* topic, byte* payload, unsigned int length);

//Defining wifi client
WiFiClient wifiClient;
PubSubClient client(MQTT_SERVER_IP, 1883, callback, wifiClient);

void setup() {
  //Initialize pins HIGH (since my relay is active low)
  pinMode(socket1Pin, OUTPUT);
  digitalWrite(socket1Pin, HIGH);
  pinMode(socket2Pin, OUTPUT);
  digitalWrite(socket2Pin, HIGH);

  //start wifi subsystem
  WiFi.begin(ssid, password);
  //attempt to connect to the WIFI network and then connect to the MQTT server
  reconnect();

  //wait a bit before starting the main loop
  delay(2000);
}



void loop(){

  //reconnect if connection is lost
  if (!client.connected() && WiFi.status() == 3) {reconnect();}

  //maintain MQTT connection
  client.loop();

  //MUST delay to allow ESP8266 WIFI functions to run
  delay(10); 
}


void callback(char* topic, byte* payload, unsigned int length) {

  //convert topic to string to make it easier to work with
  String topicStr = topic;

  //Check which socket status might have changed
  if(topicStr.substring(topicStr.lastIndexOf("/")+1) == "socket1"){
    if(payload[0] == '1'){
    digitalWrite(socket1Pin, LOW);
    client.publish("/test/confirm", "Socket 1 ON");
    }  
    //turn the light off if the payload is '0' and publish to the MQTT server a confirmation message
    else if (payload[0] == '0'){
      digitalWrite(socket1Pin, HIGH);
      client.publish("/test/confirm", "Socket 1 OFF");
    }
  }
  else if(topicStr.substring(topicStr.lastIndexOf("/")+1) == "socket2"){
    if(payload[0] == '1'){
    digitalWrite(socket2Pin, LOW);
    client.publish("/test/confirm", "Socket 2 ON");
    }  
    //turn the light off if the payload is '0' and publish to the MQTT server a confirmation message
    else if (payload[0] == '0'){
      digitalWrite(socket2Pin, HIGH);
      client.publish("/test/confirm", "Socket 2 OFF");
    }
  }
  else if(topicStr.substring(topicStr.lastIndexOf("/")+1) == "sockets"){
    if(payload[0] == '1'){
    digitalWrite(socket1Pin, LOW);
    digitalWrite(socket2Pin, LOW);
    client.publish("/test/confirm", "All Sockets ON");
    }  
    //turn the light off if the payload is '0' and publish to the MQTT server a confirmation message
    else if (payload[0] == '0'){
      digitalWrite(socket1Pin, HIGH);
      digitalWrite(socket2Pin, HIGH);
      client.publish("/test/confirm", "All Sockets OFF");
    }
  }
  else{
    int topic_len = topicStr.substring(topicStr.lastIndexOf("/")).length() + 1;
    char topicChar[topic_len];
    topicStr.substring(topicStr.lastIndexOf("/")).toCharArray(topicChar,topic_len);
    client.publish("/test/confirm", topicChar);
  }

}




void reconnect() {

  //attempt to connect to the wifi if connection is lost
  if(WiFi.status() != WL_CONNECTED){

    //loop while we wait for connection
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
    }
  }

  //make sure we are connected to WIFI before attemping to reconnect to MQTT
  if(WiFi.status() == WL_CONNECTED){
  // Loop until we're reconnected to the MQTT server
    while (!client.connected()) {
      // Generate client name based on MAC address and last 8 bits of microsecond counter
      String clientName;
      clientName += "esp8266-";
      uint8_t mac[6];
      WiFi.macAddress(mac);
      clientName += macToStr(mac);

      //if connected, subscribe to the topic(s) we want to be notified about
      if (client.connect((char*) clientName.c_str())) {
        client.subscribe(socket1Topic);
        client.subscribe(socket2Topic);
      }

      //otherwise print failed for debugging
      else{abort();}
    }
  }
}

//generate unique name from MAC addr
String macToStr(const uint8_t* mac){

  String result;

  for (int i = 0; i < 6; ++i) {
    result += String(mac[i], 16);

    if (i < 5){
      result += ':';
    }
  }

  return result;
}

