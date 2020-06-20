#include <SPI.h>
#include <mcp2515.h>


struct can_frame canRx;
struct can_frame canTx;
MCP2515 mcp2515(10);

int receive_ID = 0; // 
int sending_ID = 0; // 
const int H1 = 6;
const int H2 = 7;
const int EEP = 5; 


int pwm_val = 0; 

void prep_frame (int ID ,int data0, int data1, int data2, int data3,int  data4,int data5,int  data6,int data7){
  canTx.can_id  = ID;
  canTx.can_dlc = 8;
  canTx.data[0] = data0;
  canTx.data[1] = data1;
  canTx.data[2] = data2;
  canTx.data[3] = data3;
  canTx.data[4] = data4;
  canTx.data[5] = data5;
  canTx.data[6] = data6;
  canTx.data[7] = data7;
}


void MotorClockwise(int pwm){
  digitalWrite(H1, LOW);
  digitalWrite(H2, HIGH);
  analogWrite(EEP, pwm); 
  
}

void MotorCounterClockwise(int pwm){
  digitalWrite(H1, HIGH);
  digitalWrite(H2, LOW);
  analogWrite(EEP, pwm); 
  
}

void MotorStop(){
  digitalWrite(H1, LOW);
  digitalWrite(H2, LOW);
  
}


void setup() {
  Serial.begin(115200);

  mcp2515.reset();
  mcp2515.setBitrate(CAN_1000KBPS);
  mcp2515.setNormalMode();

  canTx.can_id  = 0x1A0;
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

states state_var = Request_Instruction;

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
        
        prep_frame (sending_ID ,0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8);
        
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
      Serial.print("Wheel Power ");
      Serial.print(canRx.data[1]);
      Serial.print(" /255");
      Serial.println();

      Serial.println();
      prep_frame (sending_ID ,0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8);
      Serial.print("Requesting NEXT instruction with device ID: ");
      Serial.print(sending_ID, HEX);
      mcp2515.sendMessage(&canTx);
      pwm_val = canRx.data[1];
      }

      if (canRx.data[0] == 0xAA){
        Serial.println("Forward");
        MotorCounterClockwise(pwm_val);     
      }
      else if (canRx.data[0] == 0xBB)
      {
        Serial.println("Backward");
        MotorClockwise(pwm_val);
      }
      else if (canRx.data[0] == 0x00)
      {
        MotorStop();
      }
  
      
      break;
  
  }
}

void loop() {
  statemachine ();
}
