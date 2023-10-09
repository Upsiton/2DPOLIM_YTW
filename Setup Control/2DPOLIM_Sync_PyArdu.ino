/*
  Sychronization of 2DPOLIM Setup by Arduino

  Producing TTL trigger pulses for sychronization of the laser modulation & liquid crystale 
  polarization rotator & video acquisition of two cameras. 
  Due to the response time of state switch of LC, the triggers which are sent to LC need to 
  be earlier than rest of the devices. Thus, two output pins (trigPin & trigLCPin) of TTL pulses.

  Inspired from exmaples from Arduino website:
  https://www.arduino.cc/

  created in January 2022
  Author: Yutong Wang


  Updates:
  - Improvement by Mr.Andreas Berger on 26.04.2022 
  - Version: 2DPOLIM_Sync_Beta0.9.ino @ 2022/08/03 Rewrite the code in defined functions.
  - Implemented more commands for setting parameters @ 2022/08/10   
  - Improved CW mode, implemented manual termination of modes @ 2022/08/15,16 
        
*/
//*****************************************************************************************************************************
/******** Declaration ********/
// Global Variables

//  {{{!!! You usually need to modify THIS part !!! For some parameters, only change them when you know what you're doing! }}}
int numScan = 3;  //[nscan:val] set number of repetition of full scan among 6 polarization orientations. Named: # of Repetition
// Set parameter of trigger pulses (time unit: ms)
int triggerPulseWidthLC = 5;     //[lcpt:val] set pulse Width of LC. Unit: ms. (Do not change it!) Named: LC Pulse Width
int LCWaitTime = 50;             //[lcwait:val] set Waiting Time (ms) for LC state switching to e.g. 25ms, i.e., interval time between LC trigger pulse and MAIN trigger pulse (for laser & Cams). Default value:25. (Do not change it!) Named: LC Wait Time
int triggerPulseWidthMain = 80;  //[mnpt:val] set Pulse Width (ms) of the MAIN trigger pulse (for laser & cameras' exposure). Named: Exposure Pulse Width
int triggerDelayTime = 50;       //[pdly:val] set Interval Time (ms) between Two adjacent Trigger Pulses (Indeed, it's delay time of the adjacent pulse. Real interval time (PRI, Pulse Repetition Interval) should be it plus pulse Width). (change only when necessary!) Named: Interval between Repetitions


//  {{{!!! DO NOT modify the following unless you know what you're doing !!!}}}
// Set output pins
// constants won't change.
//const int trigPin = 28; // set pin for sending TTL trigger pulse to Laser and 2 cameras; 28 for DUE; 8 for UNO. Discarded after improvement by Andreas! Instead, use Pin 11 & 12 in UNO/DUE.
const int trigLCPin = 9;         // set pin for triggering LC seperately; 38 for DUE; 7 for UNO; Current Pin for DUE: 9
const int buttonPin = 8;         // pin to the switch for getting pushbutton number; 22 for DUE; 12 for UNO; Current Pin for DUE: 8
const int indicatorLEDPin = 13;  // a LED used as indicator of the operation. 32 for DUE; 11 for UNO; Current Pin for DUE: 13

// Improvement made by Mr. Andreas Berger
/*
Replace the digitalWrite(trigPin, HIGH) & digitalWrite(trigPin, LOW) for sending the Main Trigger Pulse to laser & cameras.
*/
#define TRIGGER_1 11  // Pin 11: Main trigger pulse output: Camera & laser & Red LED
#define TRIGGER_2 12  // Pin 12: Main trigger pulse output: Camera & laser & Red LED

// Macros for Port Manipulation

#if defined(__SAM3X8E__)
  //Arduino DUE
#define SET_TRIGGER (PIOD->PIO_SODR = (PIO_PD8) | (PIO_PD7))  // Pin 11 = PD7 in Due; Pin 12 = PD8 in DUE
#define RESET_TRIGGER (PIOD->PIO_CODR = (PIO_PD8) | (PIO_PD7))
#elif defined(__AVR_ATmega328P__)
  // Adruino UNO / NANO ATMega328
// #define SET_TRIGGER (PORTD |= ((1<<PB3)|(1<<PB4)))       // Pin 11 = PB3 in UNO; Pin 12 = PB4 in UNO. Original code: This does not work on UNO.
// #define RESET_TRIGGER (PORTD &=~((1<<PB3)|(1<<PB4)))
// Correction by Yutong:
#define SET_TRIGGER (PORTB |= ((1 << PB3) | (1 << PB4)))  // Pin 11 = PB3 in UNO; Pin 12 = PB4 in UNO. Solution: replace PORTD => PORTB. Reason: PB3 is PORTB not PORTD. (PORTD |= ((1<<PD3)|(1<<PD4))) works at Pin 4 (PD4) & 3 (PD3). Solved on 2022.06.02.
#define RESET_TRIGGER (PORTB &= ~((1 << PB3) | (1 << PB4)))
#elif defined(__AVR_ATmega2560__) || defined(__AVR_ATmega1280__)
  // Adruino ATmega2560/ATmega1280
#define SET_TRIGGER (PORTB |= ((1 << PD6) | (1 << PD5)))
#define RESET_TRIGGER (PORTB &= ~((1 << PD6) | (1 << PD5)))
#else
#erroer Processor_not_supported
#endif
// End of Mr. Andreas Berger's code

// variables will change:
unsigned long beforeTime;   // for calculating time
unsigned long currentTime;  // for showing time of pulses
int buttonState;            // variable for reading the pushbutton status
int lastButtonState = 1;    //previous state of the button; 1 means button OFF
int pushButtonCount = 0;    //counter for the number of button presses
int charIndex;              // for locating certain char in the String command

String serialCmd;
char CWMode_flag = '0';


/******** Inertialization of Arduino ********/
// the setup function runs once when you press reset or power the board

void setup() {
  // initialize digital pin xx as an output.
  //pinMode(trigPin, OUTPUT);
  pinMode(trigLCPin, OUTPUT);
  //pinMode(22, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);  // initialize the pushbutton pin as an input; built-in 20K pullup resistors are accessed by setting the pinMode() as INPUT_PULLUP; This inverts the behavior of the INPUT mode, where HIGH means the sensor is off, and LOW means the sensor is on.
  pinMode(indicatorLEDPin, OUTPUT);
  pinMode(TRIGGER_1, OUTPUT);
  pinMode(TRIGGER_2, OUTPUT);

  Serial.begin(115200);  // initialize serial communication at 9600 bits per second. 9600 or 115200; 115200 baud
  delay(100);            // initial waiting time after power on

  while (!Serial) {  //Indicates if the specified Serial port is ready. On the boards with native USB, if (Serial) (or if(SerialUSB) on the Due) indicates whether or not the USB CDC serial connection is open.
    ;                // wait for serial port to connect. Needed for native USB
  }
  Serial.println("Arduino is ready. PUSH Button / SEND Command to start triggering......");
}

//*****************************************************************************************************************************
/******** Main Code ********/

void loop() {
  /* ========== Step 1: Count push button to initiate trigger ==========*/
  pushButtonCount = pushButtonCounter();

  /* ========== Step 2: Count down after button is pushed ==========*/
  if (pushButtonCount != 0) {  // When button is pushed

    /* ========== Step 3: Sending Trigger pulses ==========*/
    //beforeTime = millis(); // record initial time

    // Use switch / case statements
    switch (pushButtonCount) {
        /* ========== Step 3.1: Run Acquisition (Limited-Cycle) Mode ==========*/
      case 1:
        runAcquisitionMode();
        break;  // break terminates switch. The flow of control jumps to the next line following the switch statement. If no break appears, the flow of control will fall through to subsequent cases until a break is reached.

        /* ========== Step 3.2: Run Endless Mode ==========*/
      case 2:
        runEndlessMode();
        break;

        /* Run/Stop Continuous Wave Mode (turn the laser ON/OFF) */
      case 3:
        if (CWMode_flag == '0')  // Not in CW mode
        {
          CWMode_flag = runCWTriggerMode();  // Run CW mode and assign '1' to CWMode_flag
        } else if (CWMode_flag == '1')       // Already in CW mode
        {
          CWMode_flag = exitCWTriggerMode();  // Exit CW mode and assign '0' to CWMode_flag
        }
        break;

        /* Print out current parameters */
      case 4:
        printParameters();
        break;

      default:
        Serial.println("Arduino Command Error!");

    }  //end of "switch (pushButtonCount)" statement
    Serial.println("Arduino is ready. PUSH Button / SEND Command to start triggering...");
  }  // end of "if (pushButtonCount != 0){    // When button is pushed" statement
  /* At last, restore value of variables: */
  pushButtonCount = 0;  // reset it for further running

  /* Control by receiving cmd from Python via serial communication*/
  while (Serial.available() > 0) {
    //serialCmd=Serial.readString();
    serialCmd = Serial.readStringUntil('\r');
    Serial.println("Arduino received command: " + serialCmd);

    /* ========== Run Acquisition (Limited-Cycle) Mode ==========*/
    if (serialCmd == "acqm") {
      runAcquisitionMode();
    }
    /* ========== Run Endless Mode ==========*/
    else if (serialCmd == "infm") {
      runEndlessMode();
    }
    /* ========== Run/Exit Continuous Wave Mode (Immediately turn the laser ON/OFF) ==========*/
    else if (serialCmd == "cwm1" && CWMode_flag == '0') {
      CWMode_flag = runCWTriggerMode();  // Run CW mode and assign '1' to CWMode_flag
    } else if (serialCmd == "cwm0" && CWMode_flag == '1') {
      CWMode_flag = exitCWTriggerMode();  // Exit CW mode and assign '0' to CWMode_flag
    }

    /******************* Commands for setting parameters *******************/
    else if (serialCmd.startsWith("nscan:")) {
      charIndex = serialCmd.indexOf(':');
      numScan = serialCmd.substring(charIndex + 1).toInt();   //Get the substring of command String after ':' (val). Converts the substring to an integer and assign to parameter.
      Serial.println("Set '# of Repetition(var:numScan)' to:" + String(numScan));  // Appends the parameter to a String
    }

    else if (serialCmd.startsWith("lcpt:")) {
      charIndex = serialCmd.indexOf(':');
      triggerPulseWidthLC = serialCmd.substring(charIndex + 1).toInt();  //Get the substring of command String after ':' (val). Converts the substring to an integer and assign to parameter.
      Serial.println("Set 'LC Pulse Width(var:triggerPulseWidthLC)' to:" + String(triggerPulseWidthLC) + "ms");
    }

    else if (serialCmd.startsWith("lcwait:")) {
      charIndex = serialCmd.indexOf(':');
      LCWaitTime = serialCmd.substring(charIndex + 1).toInt();  //Get the substring of command String after ':' (val). Converts the substring to an integer and assign to parameter.
      Serial.println("Set 'LC Wait Time(var:LCWaitTime)' to:" + String(LCWaitTime) + "ms");
    }

    else if (serialCmd.startsWith("mnpt:")) {
      charIndex = serialCmd.indexOf(':');
      triggerPulseWidthMain = serialCmd.substring(charIndex + 1).toInt();  //Get the substring of command String after ':' (val). Converts the substring to an integer and assign to parameter.
      Serial.println("Set 'Exposure Pulse Width(var:triggerPulseWidthMain)' to:" + String(triggerPulseWidthMain) + "ms");
    }

    else if (serialCmd.startsWith("pdly:")) {
      charIndex = serialCmd.indexOf(':');
      triggerDelayTime = serialCmd.substring(charIndex + 1).toInt();  //Get the substring of command String after ':' (val). Converts the substring to an integer and assign to parameter.
      Serial.println("Set 'Interval between Repetitions(var:triggerDelayTime)' to:" + String(triggerDelayTime) + "ms");
    }

    else if (serialCmd == "parm?") {
      printParameters();
    }
    /******************* end of the block *******************/

    else {
      Serial.println("Arduino Command Error!");
    }
    Serial.println("Arduino is ready. PUSH Button / SEND Command to start triggering...");
  }
}

//*****************************************************************************************************************************
// Function definations:

int pushButtonCounter() {
  /* ========== Step 1: Detect push button to initiate trigger ==========*/
  buttonState = digitalRead(buttonPin);
  int pushButtonCountValue = 0;
  if (buttonState != lastButtonState && buttonState == LOW) {  // change in button state and button is pushed; buttonState == LOW means button is pushed due to INPUT_PULLUP is used in current circuit.
    pushButtonCountValue = 1;
    beforeTime = millis();
    digitalWrite(indicatorLEDPin, HIGH);
    delay(10);
    digitalWrite(indicatorLEDPin, LOW);

    while (millis() - beforeTime < 1.0 * 1000) {  // stay in the loop and count push button within certain ms after the first pushbutton
      lastButtonState = buttonState;
      delay(50);  // delay a little bit to avoid bouncing
      buttonState = digitalRead(buttonPin);
      if (buttonState != lastButtonState && buttonState == LOW) {  // determine another push of button
        pushButtonCountValue++;
        digitalWrite(indicatorLEDPin, HIGH);
        delay(10);
        digitalWrite(indicatorLEDPin, LOW);
      }
    }
    Serial.print("# of pushing button: ");
    Serial.println(pushButtonCountValue);
  }
  lastButtonState = buttonState;  // avoid count when keep pushing the button, count for only 1 in this case
  delay(50);                      // delay a little bit to avoid bouncing
  return pushButtonCountValue;
}

void countdown() { /*Count down of 3s:*/
  delay(100);

  for (int i = 3; i > 0; i--) {
    Serial.println("Triggering will start in: " + String(i) + " seconds!");
    digitalWrite(indicatorLEDPin, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(indicatorLEDPin, LOW);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
  }

  Serial.println("Triggering start!!!");
  digitalWrite(indicatorLEDPin, HIGH);  //turn on the indicator LED during triggering
                                        //Serial.println(pushButtonCount);
}

void runAcquisitionMode()  // Run in image acquisition mode with numScan sequences of trigger
{
  int totalShots = 7 * numScan;  // total number of pulses it will shot; Each full scanning of all LC states. 6 plus 1 of null state (0V).
  int numCycle = 0;
  int iShot = 1;      // count number of pulses
  CWMode_flag = '0';  // Firstly, break the possible CW Mode and set CWMode flag down
  RESET_TRIGGER;      // turn off trigger

  delay(100);
  Serial.println("Run Acquisition (Limited-Cycle) Mode!");
  delay(100);
  Serial.print("# of Cycles: ");
  Serial.println(numScan);

  countdown();            // countdown of 3s
  beforeTime = millis();  // record initial time

  for (int iShot = 1; iShot <= totalShots; iShot++) {  // leave initialization part empty in for statement for runing only once in the loop(){}

    // First, trigger the LC Rotator 50 ms earlier than Laser & Cameras trigger
    digitalWrite(trigLCPin, HIGH);       // Set pin to 3.3V: Beginning of LC trigger pulse
    delay(triggerPulseWidthLC);          // LC pulse width
    digitalWrite(trigLCPin, LOW);        // Set pin to 0V: End of LC trigger pulse
    
    delay(LCWaitTime);                   // LC pulse is sent 50ms in advance of Laser & Cameras:

    // Second, send the main trigger pulse for Laser & Cameras
    //digitalWrite(trigPin, HIGH);         // Beginning of Main trigger pulse (for laser & Cams). (Replaced by SET_TRIGGER;)
    SET_TRIGGER;
    digitalWrite(LED_BUILTIN, HIGH);     // Turn the LED indicator on (HIGH is the voltage level)
    delay(triggerPulseWidthMain);        // Pulse width of Main trigger pulse (for laser & Cams)
    
    currentTime = millis() - beforeTime; // Count current time when Main trigger pulse is send

    //digitalWrite(trigPin, LOW);        // End of Main trigger pulse
    RESET_TRIGGER;
    digitalWrite(LED_BUILTIN, LOW);      // Turn the LED indicator off (OFF is the voltage level)
    //digitalWrite(trigLCPin, LOW);

    delay(triggerDelayTime);             // Wait for 50 ms as interval time between pulses

    // ====== Every 7th shot will trigger LC to NULL state (state1 = 0V). Recover the LC from high voltage to 0V. Get ready for the next cycle. Without "Main trigger" to laser & cams
    // Also detecting buttonState & serial input after every 7th shot. Disable it if it causes unacceptable time delay!!!
    if (iShot % 7 == 0) {
      delay(50);  // Longer waiting time (50ms) for LC fully relaxed from high voltage to 0V.
      Serial.print("A full scan complete! #cycle: ");
      Serial.println(numCycle + 1);
      numCycle++;  // count number of cycle

      //=== Read Push-button state for early termination
      // Pushing the button during process to break. In current circuit, Push button: buttonState == LOW, due to INPUT_PULLUP is used.
      buttonState = digitalRead(buttonPin);
      if (buttonState == LOW) {
        digitalWrite(indicatorLEDPin, LOW);
        Serial.println("Stopped by user!");
        lastButtonState = buttonState;
        break;
      }

      //=== Read serial input for early termination. Stop by sending command "acqm0". Disable it if it causes unacceptable time delay!!!
      else if (Serial.available() > 0) {
        serialCmd = Serial.readStringUntil('\r');
        Serial.println("Arduino received command: " + serialCmd);

        if (serialCmd == "acqm0") {
          Serial.println("Stopped by user!");
          break;
        } else {
          Serial.println("Arduino Command Error: Need to stop current Mode by sending 'acqm0' or push-button before further cmd. ");
        }
      }
    }  // end of: if (iShot % 7 == 0){}
    // Not 7th shot:
    else {
      Serial.print("Current shot: ");
      Serial.print(String(iShot - numCycle) + "/" + String(6 * numScan));  // print out the number of shots
      Serial.println(" @time: " + String(currentTime) + "ms");             // print out time after process start
    }                                                                      // end of: if (iShot % 7 == 0){} else{}

  }  // end of for loop

  digitalWrite(indicatorLEDPin, LOW);  // turn off the indicator LED after the triggering finishes
  Serial.println("Done!");
  //Serial.println("Arduino is ready. PUSH Button / SEND Command to start triggering...");
  //pushButtonCount = 0;
}

void runEndlessMode()  // Sendling endless triggers until be terminated by user
{
  /* ========== Step 3.2: Endless Mode ==========*/
  int iShot = 1;      // count number of pulses
  CWMode_flag = '0';  // Firstly, break the possible CW Mode and set CWMode flag down
  RESET_TRIGGER;      // turn off trigger

  delay(100);
  Serial.println("Run Endless Trigger Mode!");

  countdown();            // countdown of 3s
  beforeTime = millis();  // record initial time
  do {                    //Serial.println(pushButtonCount);
    //Serial.println("Case2 works");

    // First, trigger the LC 50 ms earlier of laser & cams

    digitalWrite(trigLCPin, HIGH);
    delay(triggerPulseWidthLC);  // LC pulse Width
    digitalWrite(trigLCPin, LOW);
    delay(LCWaitTime);  // LC pulse is sent in advance of laser & Cams

    // Second, sending the main trigger pulse for LASER & 2 CAMs

    //digitalWrite(trigPin, HIGH); // turn the pin on to high voltage (3.3V)
    SET_TRIGGER;
    digitalWrite(LED_BUILTIN, HIGH);      // turn the LED on (HIGH is the voltage level)
    delay(triggerPulseWidthMain);         // pulse Width of main trigger pulse (for laser & Cams)
    currentTime = millis() - beforeTime;  // count current time when main trigger pulse is send

    //digitalWrite(trigPin, LOW);
    RESET_TRIGGER;
    digitalWrite(LED_BUILTIN, LOW);  // turn the LED off (OFF is the voltage level)

    buttonState = digitalRead(buttonPin);

    Serial.print("Current shot: ");
    Serial.print(iShot++);
    Serial.println(" @time: " + String(currentTime) + "ms");  // print out time after process start

    delay(triggerDelayTime);  // wait for xx millisecond as interval time of pulses

    // ========== Alternative of Push-button: Send Command 'infm0' to Stop CW Mode ==========
    if (Serial.available() > 0) {
      serialCmd = Serial.readStringUntil('\r');
      Serial.println("Arduino received command: " + serialCmd);

      if (serialCmd == "infm0") {
        break;
      } else {
        Serial.println("Arduino Command Error: Need to stop current Mode by sending infm0 or push-button before further cmd. ");
      }
    }

  } while (buttonState == HIGH);  // push the button during Endless mode to break. In current circuit, Push button: buttonState == LOW, due to INPUT_PULLUP is used.
  digitalWrite(indicatorLEDPin, LOW);
  Serial.println("Endless Mode is stopped by user!");
  //Serial.println("Arduino is ready. PUSH Button / SEND Command to start triggering...");
  lastButtonState = buttonState;
}

char runCWTriggerMode()  // Sendling endless continuous wave (constant high voltage state) triggers until be terminated by user
{
  // ========== CW Mode ==========
  delay(10);
  Serial.println("Run Continuous Wave Trigger Mode!");
  countdown();  // countdown of 3s
  //buttonState = digitalRead(buttonPin);

  // Turn on the main trigger for LASER & 2 CAMs
  //digitalWrite(trigPin, HIGH); // turn the pin on to high voltage (3.3V):
  SET_TRIGGER;
  digitalWrite(LED_BUILTIN, HIGH);                                    // turn the LED on (HIGH is the voltage level)
  currentTime = millis() - beforeTime;                                // count current time
  Serial.println("CW Mode ON @time: " + String(currentTime) + "ms");  // print out time after process start
  Serial.println(".-.-.");                                            //Tell python stop reading serial. Morse code for "End of transmission/New page"
  return '1';                                                         // assign '1' to CWMode_flag
}

char exitCWTriggerMode()  // Terminate endless continuous wave (constant high voltage state) triggers
{
  //digitalWrite(trigPin, LOW);
  RESET_TRIGGER;                   // turn off trigger
  digitalWrite(LED_BUILTIN, LOW);  // turn the LED off (OFF is the voltage level)
  Serial.println("CW Mode is stopped by user!");
  currentTime = millis() - beforeTime;  // count current time
  Serial.println("@time: " + String(currentTime) + "ms");
  Serial.println("Arduino is ready. PUSH Button / SEND Command to start triggering...");
  Serial.println(".-.-.");  //Tell python stop reading serial. Morse code for "End of transmission/New page"
  return '0';               // assign '0' to CWMode_flag
}


// This implementation is replaced by runCWTriggerMode() and exitCWTriggerMode(), and deprecated in version 2022.08.15
/*
void runCWTriggerMode() // Sendling endless continuous wave (constant high voltage state) triggers until be terminated by user
{
  // ========== CW Mode ==========
  delay(100);
  Serial.println("Run Continuous Wave Trigger Mode!");  
  
  countdown(); // countdown of 3s 
  //delay(1000);
  buttonState = digitalRead(buttonPin);

  // Turn on the main trigger for LASER & 2 CAMs
  //digitalWrite(trigPin, HIGH); // turn the pin on to high voltage (3.3V)
  SET_TRIGGER; 
  digitalWrite(LED_BUILTIN, HIGH); // turn the LED on (HIGH is the voltage level)
  currentTime = millis()-beforeTime; // count current time
  Serial.println("CW Mode ON @time: " + String(currentTime) + "ms");  // print out time after process start
  //Serial.println(buttonState);

  while (buttonState == HIGH) // push the button during cw mode to break. In current circuit, Push button: buttonState == LOW, due to INPUT_PULLUP is used.
  {  
    currentTime = millis()-beforeTime; // count current time
    Serial.println("Arduino is IN the CW Mode while loop: " + String(currentTime) + "ms"); // Test the delay time caused by detecting buttonState & Serial.available(). Resulting delay time is < 1 ms.

    buttonState = digitalRead(buttonPin); // stop the cw mode until button is pushed
    delay(5);
    // ========== Or Send Command to Stop CW Mode ==========
    if (Serial.available()>0) 
    {
      serialCmd=Serial.readStringUntil('\r');
      Serial.println("Arduino received command: "+serialCmd);
      
      if(serialCmd=="cwm0")
      {
        break;      
      }
      else 
      {
        Serial.println("Arduino Command Error: Need to stop CW Mode by sending cwm0 or push-button before further cmd. ");
      } 
    } 
  }
  lastButtonState = buttonState;
  //Serial.println("Arduino is OUT of the CW Mode while loop");
  
  //digitalWrite(trigPin, LOW);
  RESET_TRIGGER; // turn off trigger
  digitalWrite(LED_BUILTIN, LOW);  // turn the LED off (OFF is the voltage level)
  Serial.println("CW Mode is stopped by user!");
  currentTime = millis()-beforeTime; // count current time
  Serial.println("@time: " + String(currentTime) + "ms"); 
  Serial.println("Arduino is ready. PUSH Button / SEND Command to start triggering...");   
}
*/

void printParameters() {  // Print out current setting of trigger pulse parameters.
  Serial.println("Print current setting of trigger pulse parameters:");
  Serial.println("# of Repetition(var:numScan) = " + String(numScan));                                     // set number of full scan of 6 polarization orientations. # of Repetition
  Serial.println("LC Pulse Width(var:triggerPulseWidthLC) = " + String(triggerPulseWidthLC) + "ms");      // set pulse Width of LC. Unit: ms
  Serial.println("LC Wait Time(var:LCWaitTime) = " + String(LCWaitTime) + "ms");                        // set Waiting Time (ms) for LC state switching to e.g. 25ms, i.e., interval time between LC trigger pulse and MAIN trigger pulse (for laser & Cams). Default value:25
  Serial.println("Exposure Pulse Width(var:triggerPulseWidthMain) = " + String(triggerPulseWidthMain) + "ms");  // set Pulse Width (ms) of the MAIN trigger pulse (for laser & cameras' exposure)
  Serial.println("Interval between Repetitions(var:triggerDelayTime) = " + String(triggerDelayTime) + "ms");            // set Interval Time (ms) between Two adjacent Trigger Pulses (Indeed, it's delay time of the adjacent pulse. Real interval time (PRI, Pulse Repetition Interval) should be it plus pulse Width).
}
// The end of code.

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/*Previous Test*/
/*Main code: Sending the trigger forever and ever. */
