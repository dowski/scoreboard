#include <LedControl.h>

#define D1 5
#define D2 4
#define D3 0
#define D4 2
#define D5 14 // SCK
#define D6 12 // MISO
#define D7 13 // MOSI

LedControl lc = LedControl(D1, D2, D3, 1);

void setup() {
  //Serial.begin(115200);
  //Serial.println("\n\nWake up");
  
  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.setScanLimit(0,3);
  
  for (int i=0; i < 1000; i++) {
    int ones = i % 10;
    int tens = (i/10) % 10;
    int hundreds = i/100;
    lc.setDigit(0,0,hundreds,false);
    lc.setDigit(0,1,tens,false);
    lc.setDigit(0,2,ones, false);
    delay(100);
  }
  int sleepSeconds = 5;
  //Serial.printf("Sleep for %d seconds\n\n", sleepSeconds);
  
  // Connect pin 8 to RST to wake up (somehow this does that)
  pinMode(8, WAKEUP_PULLUP);
  // convert to microseconds
  ESP.deepSleep(sleepSeconds * 1000000, WAKE_RF_DEFAULT);
}

void loop() {
}
