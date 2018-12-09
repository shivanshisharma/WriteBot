//------------------------------------------------------------------------------
// 4 Axis CNC Demo  - supports CNCShieldV3 on arduino UNO
// dan@marginallyclever.com 2013-10-28
// Modified by Søren Vedel
// sorenvedel@gmail.com 2015-06-19
// Modified by Cristian Leiva
// cristianleiva@gmail.com 2016-04-28
// add Support cncshield - feed rate in mm/min

//------------------------------------------------------------------------------
// Copyright at end of file.
// please see http://www.github.com/MarginallyClever/GcodeCNCDemo for more information.

#include <stdio.h>
#include <stdlib.h>
#include <Stepper.h>
#include <stdbool.h>
Stepper penMotor(150, 8, 9, 10, 11);


//------------------------------------------------------------------------------
// CONSTANTS
//------------------------------------------------------------------------------
//#define VERBOSE              (1)       // add to get a lot more serial output.

#define VERSION              (2)                      // firmware version
#define BAUD                 (14400)                 // How fast is the Arduino talking?(BAUD Rate of Arduino)
#define MAX_BUF              (64)                     // What is the longest message Arduino can store?
#define STEPS_PER_TURN       (200)                    // depends on your stepper motor.  most are 200.
#define STEPS_PER_MM         (STEPS_PER_TURN*16/0.8)  // (400*16)/0.8 with a M5 spindle
#define MAX_FEEDRATE         (1000000)
#define MIN_FEEDRATE         (1)
#define NUM_AXIES            (2)
#define MS1                  (6)
#define MS2                  (7)


//------------------------------------------------------------------------------
// STRUCTS
//------------------------------------------------------------------------------
// for line()
typedef struct {
  long delta;  // number of steps to move
  long absdelta;
  long over;  // for dx/dy bresenham calculations
} Axis;


typedef struct {
  int step_pin;
  int dir_pin;
  //int enable_pin;
  //int limit_switch_pin;
} Motor;


//------------------------------------------------------------------------------
// GLOBALS
//------------------------------------------------------------------------------
Axis a[NUM_AXIES];  // for line()
Axis atemp;  // for line()
Motor motors[NUM_AXIES];

char buffer[MAX_BUF];  // where we store the message until we get a ';'
int sofar;  // how much is in the buffer

// speeds
float fr=0;  // human version
long step_delay;  // machine version

float px,py;  // position

// settings
char mode_abs=1;  // absolute mode?

long line_number=0;

int penState = 0;




//------------------------------------------------------------------------------
// METHODS
//------------------------------------------------------------------------------


/**
 * delay for the appropriate number of microseconds
 * @input ms how many milliseconds to wait
 */
void pause(long ms) {
  delay(ms/1000);
  delayMicroseconds(ms%1000);  // delayMicroseconds doesn't work for values > ~16k.
}


/**
 * Set the feedrate (speed motors will move)
 * @input nfr the new speed in steps/second
 */
void feedrate(float nfr) {
  nfr = nfr*STEPS_PER_MM/60; 
  if(fr==nfr) return;  // same as last time?  quit now.

  if(nfr>MAX_FEEDRATE || nfr<MIN_FEEDRATE) {
    return;
  }
  step_delay = MAX_FEEDRATE/nfr;
  fr=nfr;
}


/**
 * Set the logical position
 * @input npx new position x
 * @input npy new position y
 */
void position(float npx,float npy) {
  // here is a good place to add sanity tests
  px=npx;
  py=npy;
 
}


/**
 * Uses bresenham's line algorithm to move both motors
 * @input newx the destination x position
 * @input newy the destination y position
 **/
void line(float newx,float newy) {
  Serial.println(newx);
  Serial.println(newy);
  a[0].delta = (newx-px)*STEPS_PER_MM;
  a[1].delta = (newy-py)*STEPS_PER_MM;
  Serial.println(a[0].delta);
  Serial.println(a[1].delta);

  
  long i,j,maxsteps=0;

  for(i=0;i<NUM_AXIES;++i) {
    a[i].absdelta = abs(a[i].delta);
    a[i].over=0;
    if( maxsteps < a[i].absdelta ) maxsteps = a[i].absdelta;
    // set the direction once per movement
    digitalWrite(motors[i].dir_pin,a[i].delta>0?HIGH:LOW);
  }
  
  long dt = MAX_FEEDRATE/5000;
  long accel = 1;
  long steps_to_accel = dt - step_delay;
  if(steps_to_accel > maxsteps/2 ) 
    steps_to_accel = maxsteps/2;
    
  long steps_to_decel = maxsteps - steps_to_accel;

  for( i=0; i<maxsteps; ++i ) {
    for(j=0;j<NUM_AXIES;++j) {
      a[j].over += a[j].absdelta;
      if(a[j].over >= maxsteps) {
        a[j].over -= maxsteps;
        
        digitalWrite(motors[j].step_pin,HIGH);
        delayMicroseconds(800);
        digitalWrite(motors[j].step_pin,LOW);
      }
    }

    if(i<steps_to_accel) {
      dt -= accel;
    }
    if(i>=steps_to_decel) {
      dt += accel;
    }
    delayMicroseconds(dt);
  }

  position(newx,newy);

}

void penUp(void){
    if (!penState) {
      penMotor.step(150);
      penState = 1;
      delay(1000);
    } else {
      Serial.println("Pen is already up");
    }
}

void penDown(void){
    if (penState) {
      penMotor.step(-150);
      penState = 0;
      delay(1000);
    } else {
      Serial.println("Pen is already down");
    }
}
/**
 * Look for character /code/ in the buffer and read the float that immediately follows it.
 * @return the value found.  If nothing is found, /val/ is returned.
 * @input code the character to look for.
 * @input val the return value if /code/ is not found.
 **/
float parseNumber(char code,float val) {
  char *ptr=buffer;  // start at the beginning of buffer
  while((long)ptr > 1 && (*ptr) && (long)ptr < (long)buffer+sofar) {  // walk to the end
    if(*ptr==code) {  // if you find code on your walk,
      return atof(ptr+1);  // convert the digits that follow into a float and return it
    }
    ptr=strchr(ptr,' ')+1;  // take a step from here to the letter after the next space
  }
  return val;  // end reached, nothing found, return default val.
}


/**
 * Read the input buffer and find any recognized commands.  One G or M command per line.
 */
void processCommand() {
  int cmd = parseNumber('G',-1);
  if (cmd == 0) {
    Serial.println("Zero");
    penUp();
    line( parseNumber('X',(mode_abs?px:0)) + (mode_abs?0:px),
          parseNumber('Y',(mode_abs?py:0)) + (mode_abs?0:py));
  } else if(cmd == 1) {
    Serial.println("One");
    penDown();
    line( parseNumber('X',(mode_abs?px:0)) + (mode_abs?0:px),
          parseNumber('Y',(mode_abs?py:0)) + (mode_abs?0:py));
  } else {
    Serial.println("Invalid command G" + cmd);
  }
//  switch(cmd) {
//    
//  case  0:
//    Serial.println("Zero");
//    penUp();
//    Serial.println("Pen up done");
//    line( parseNumber('X',(mode_abs?px:0)) + (mode_abs?0:px),
//          parseNumber('Y',(mode_abs?py:0)) + (mode_abs?0:py));
//  case  1: // line
//    Serial.println("One");
//    penDown();
//    Serial.println("Pen down done");
//    line( parseNumber('X',(mode_abs?px:0)) + (mode_abs?0:px),
//          parseNumber('Y',(mode_abs?py:0)) + (mode_abs?0:py));
//    break;
//  default:
//        break;
//  }
}


/**
 * prepares the input buffer to receive a new message and tells the serial connected device it is ready for more.
 */
void ready() {
  sofar=0;  // clear input buffer
}


/**
 * set up the pins for each motor
 * Pins fits a CNCshieldV3.xx
 */
void motor_setup() {
  motors[0].step_pin=3;     //x-axis motor
  motors[0].dir_pin=2;
  //motors[0].enable_pin=8;
  //motors[0].limit_switch_pin=9;

  motors[1].step_pin=5;     //y-axis motor
  motors[1].dir_pin=4;
  //motors[1].enable_pin=8;
  //motors[1].limit_switch_pin=10;

  //motors[2].step_pin=4;
  //motors[2].dir_pin=7;
//  motors[2].enable_pin=8;
//  motors[2].limit_switch_pin=11;
//
//  motors[3].step_pin=12;
//  motors[3].dir_pin=13;
//  motors[3].enable_pin=8;
//  motors[3].limit_switch_pin=11;
   
  pinMode(MS1,OUTPUT);
  pinMode(MS2,OUTPUT);

  
  int i;
  for(i=0;i<NUM_AXIES;++i) {  
    // set the motor pin & scale
    pinMode(motors[i].step_pin,OUTPUT);
    pinMode(motors[i].dir_pin,OUTPUT);
    //pinMode(motors[i].enable_pin,OUTPUT);
  }
}

//
//void motor_enable() {
//  int i;
//  for(i=0;i<NUM_AXIES;++i) {  
//    digitalWrite(motors[i].enable_pin,LOW);
//  }
//}
//
//
//void motor_disable() {
//  int i;
//  for(i=0;i<NUM_AXIES;++i) {  
//    digitalWrite(motors[i].enable_pin,HIGH);
//  }
//}


/**
 * First thing this machine does on startup.  Runs only once.
 */
void setup() {
  Serial.begin(BAUD);  // open coms

  motor_setup();
  //motor_enable();


  digitalWrite(MS1, LOW);           // configure to full step
  digitalWrite(MS2, LOW);

  penMotor.setSpeed(100);
  
  position(0,0);  // set starting position
  feedrate(1000);  // set default speed
  ready();
}


/**
 * After setup() this machine will repeat loop() forever.
 */
void loop() {

  
  // listen for serial commands
  while(Serial.available() > 0) {  // if something is available
    char c=Serial.read();  // get it
    if(sofar<MAX_BUF-1) buffer[sofar++]=c;  // store it
    delay(1000);
    if(c=='~') {
      // entire message received
      Serial.println("Done");
      Serial.flush();
      buffer[sofar]=0;  // end the buffer so string functions work right
      processCommand();  // do something with the command
      Serial.println("09");
      Serial.flush();
      ready();
    }
  }
}

//String myString = Serial.readString();
//  Serial.println(myString);
//  //delay(1000);
//  char * buf = (char*) malloc(sizeof(char) *myString.length()+1);
//  Serial.println(myString);


/**
* This file is part of GcodeCNCDemo.
*
* GcodeCNCDemo is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* GcodeCNCDemo is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with Foobar. If not, see <http://www.gnu.org/licenses/>.
*/
