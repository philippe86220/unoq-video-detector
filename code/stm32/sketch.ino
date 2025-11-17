#include <Arduino.h>
#include <Arduino_RouterBridge.h>

const int ledPin = LED_BUILTIN;

void setLedState(bool state) {
  // LED active LOW : true = ON -> LOW, false = OFF -> HIGH
  digitalWrite(ledPin, state ? LOW : HIGH);

  Monitor.print("[C++] setLedState(");
  Monitor.print(state ? "true" : "false");
  Monitor.println(")");
}

void setup() {
  pinMode(ledPin, OUTPUT);

  // LED éteinte au démarrage
  digitalWrite(ledPin, HIGH);

  Bridge.begin();
  Monitor.begin();
  Bridge.provide("setLedState", setLedState);

  Monitor.println("[C++] setup terminé, LED à OFF");
}

void loop() {
  delay(10);
}

