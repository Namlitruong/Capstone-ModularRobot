#include <QTRSensors.h>
#include <SPI.h>
#include <mcp2515.h>
#include <PIDController.h>


struct can_frame canRx;
struct can_frame canTx;
MCP2515 mcp2515(10);
//int device_ID = 0x000;

int receive_ID = 000; // 0x0A1
int sending_ID = 000; // 0X1A1

//int receive_ID = 162; // 0x0A2
//int sending_ID = 418; // 0X1A2

int b[3];
QTRSensors qtr;

const uint8_t SensorCount = 5;
uint16_t sensorValues[SensorCount];

void prep_frame (int ID ,int DLC, int data0, int data1, int data2, int data3,int  data4,int data5,int  data6,int data7){
  canTx.can_id  = ID;
  canTx.can_dlc = DLC;
  canTx.data[0] = data0;
  canTx.data[1] = data1;
  canTx.data[2] = data2;
  canTx.data[3] = data3;
  canTx.data[4] = data4;
  canTx.data[5] = data5;
  canTx.data[6] = data6;
  canTx.data[7] = data7;
}


void setup()
{
 
  
  // configure the sensors
  qtr.setTypeRC();
  qtr.setSensorPins((const uint8_t[]){7,6,5,4,3}, SensorCount);
  qtr.setEmitterPin(2);

  delay(50);
  
  qtr.calibrate();

  Serial.begin(9600);

  //Set up CAN communication 

  mcp2515.reset();
  mcp2515.setBitrate(CAN_1000KBPS);
  mcp2515.setNormalMode();

  canTx.can_id  = 0x1F0;
  canTx.can_dlc = 8;
  canTx.data[0] = 0xE1;
  canTx.data[1] = 0xE2;
  canTx.data[2] = 0xE3;
  canTx.data[3] = 0xE4;
  canTx.data[4] = 0xE5;
  canTx.data[5] = 0xE6;
  canTx.data[6] = 0xE6;
  canTx.data[7] = 0xE7;


  canRx.can_id  = 0x000;
  canRx.can_dlc = 8;
  canRx.data[0] = 0x00;
  canRx.data[1] = 0x00;
  canRx.data[2] = 0x00;
  canRx.data[3] = 0x00;
  canRx.data[4] = 0x00;
  canRx.data[5] = 0x00;
  canRx.data[6] = 0x00;
  canRx.data[7] = 0x00;

  Serial.println("------- BEGIN ----------");

 
}

typedef enum{
  Request_Confirmation, 
  Request_Instruction, 
  }states; 
states state_var = Request_Confirmation;


void statemachine (void) {

  switch (state_var)
  {
    case Request_Confirmation:
      //If a message is received
      if (mcp2515.readMessage(&canRx) == MCP2515::ERROR_OK){
        //If the message is from the Brain 
        if (canRx.can_id == 160 ){
        Serial.println();
        Serial.println("***Connected to brain***"); //Announcing Connection
        
        for (int i = 0; i < canRx.can_dlc; i++)  { // print the data
        Serial.print(canRx.data[i], HEX);
        Serial.print(" ");
        }
        Serial.println();
        Serial.println("______Did something_______");
        
        receive_ID = canRx.can_id + canRx.data[0] ;
        sending_ID = canRx.can_id + canRx.data[0]+ 256; //Modify the device ID according to the brain assigned ID
        
        prep_frame (sending_ID ,8,0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8);
        
        mcp2515.sendMessage(&canTx); //Send the first instruction request 

        
        Serial.println("Requesting FIRST instruction with device ID: ");
        Serial.println(sending_ID, HEX);
        

        state_var = Request_Instruction; //Update the state machine to next state
        }
        
        //Message is not from the BRAIN
        else {
          Serial.println("Not Brain _ Resending request");
        //Serial.print("Requesting instruction ");
        //mcp2515.sendMessage(&canTx);  
        }
      }
      // If message NOT received --> Resend request with interval 1s
      else{
        Serial.println("Waiting  _ Identified as SENSOR");
        Serial.println(canTx.can_id,HEX);
        //Serial.print("Requesting instruction ");
        
        mcp2515.sendMessage(&canTx);
        delay(1000);
      }
      break;


    case Request_Instruction: 
        
      
     if (mcp2515.readMessage(&canRx) == MCP2515::ERROR_OK && canRx.can_id == receive_ID){
      Serial.println("--------------------------------------------------------------------------------");
      Serial.println("***Instruction Received***");
      //  [0] direction, [1] pwm 
//      update_position();
//      Serial.print("Send sensors values with ID: ");
//      Serial.print(sending_ID, HEX);
//      mcp2515.sendMessage(&canTx);

      }    

      update_position();
      Serial.print("Send sensors values with ID: ");
      Serial.print(sending_ID, HEX);
      mcp2515.sendMessage(&canTx);
      Serial.println();
      delay(500);
      break;
  
      
      break;
  
  }
}
//
//void update_position (){
//  uint16_t position = qtr.readLineBlack(sensorValues);
//  
//  if (position <= 15){
//      b[0] = input;
//      b[1] = 0;
//      b[2] = 0; 
//  }
//  else {
//      b[0] = position % 16;
//      b[1] = int(position/16) % 16;
//      b[2] = int(position/16/16) %16;
//  }
//
//  prep_frame (sending_ID ,b[2], b[1], b[0]);
//}

void update_position (){
  uint16_t position = qtr.readLineBlack(sensorValues);
  
  int value = map(position, 0, 4000, 0, 255);
  Serial.print(position);
  Serial.print("      ");
  Serial.print( value, HEX);
  prep_frame (sending_ID ,8,value, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8);
}
void loop()
{
  statemachine();
  
}
