# Code STM32 – `sketch.ino`

Ce fichier contient le code qui tourne sur le cœur **STM32** de la **UNO Q**.  
Son rôle est très simple :

- recevoir des ordres du cœur Linux via le **Bridge** ;
- allumer ou éteindre la **LED_BUILTIN** selon ces ordres.

Ce sketch travaille de pair avec le code Python décrit dans `code/python/README.md`  
(qui appelle `bridge.call("setLedState", True/False)`).

---

## Code complet

```cpp
#include <Arduino.h>
#include <Arduino_RouterBridge.h>

const int ledPin = LED_BUILTIN;

// -----------------------------------------------------------------------------
// Fonction appelée depuis le cœur Linux via Bridge.call("setLedState", ...)
// -----------------------------------------------------------------------------
void setLedState(bool state) {
  // Sur la UNO Q, la LED est câblée en "active LOW" :
  // - LOW  -> LED allumée
  // - HIGH -> LED éteinte
  //
  // On décide donc :
  //   state == true  -> LED ON  (LOW)
  //   state == false -> LED OFF (HIGH)
  digitalWrite(ledPin, state ? LOW : HIGH);

  // Petit message sur le moniteur (facultatif, surtout pour le debug)
  Monitor.print("[C++] setLedState(");
  Monitor.print(state ? "true" : "false");
  Monitor.println(")");
}

void setup() {
  // Configure la broche de la LED en sortie
  pinMode(ledPin, OUTPUT);

  // On éteint la LED au démarrage (HIGH puisque active LOW)
  digitalWrite(ledPin, HIGH);

  // Initialise le Bridge (communication avec le cœur Linux)
  Bridge.begin();

  // Initialise le moniteur série côté STM32 (console dans App Lab)
  Monitor.begin();

  // Expose la fonction setLedState au cœur Linux.
  // Côté Python, on pourra appeler :
  //    bridge.call("setLedState", True)
  //    bridge.call("setLedState", False)
  Bridge.provide("setLedState", setLedState);

  Monitor.println("[C++] STM32 prêt, Bridge initialisé");
}

void loop() {
  // Pas de logique particulière côté STM32 :
  // tout est déclenché par les appels Bridge (setLedState)
  delay(10);
}

# Code STM32 – `sketch.ino`

Ce fichier contient le code qui tourne sur le cœur **STM32** de la **UNO Q**.  
Son rôle est très simple :

- recevoir des ordres du cœur Linux via le **Bridge** ;
- allumer ou éteindre la **LED_BUILTIN** selon ces ordres.

Ce sketch travaille de pair avec le code Python décrit dans `code/python/README.md`  
(qui appelle `bridge.call("setLedState", True/False)`).

---

## Code complet

```cpp
#include <Arduino.h>
#include <Arduino_RouterBridge.h>

const int ledPin = LED_BUILTIN;

// -----------------------------------------------------------------------------
// Fonction appelée depuis le cœur Linux via Bridge.call("setLedState", ...)
// -----------------------------------------------------------------------------
void setLedState(bool state) {
  // Sur la UNO Q, la LED est câblée en "active LOW" :
  // - LOW  -> LED allumée
  // - HIGH -> LED éteinte
  //
  // On décide donc :
  //   state == true  -> LED ON  (LOW)
  //   state == false -> LED OFF (HIGH)
  digitalWrite(ledPin, state ? LOW : HIGH);

  // Petit message sur le moniteur (facultatif, surtout pour le debug)
  Monitor.print("[C++] setLedState(");
  Monitor.print(state ? "true" : "false");
  Monitor.println(")");
}

void setup() {
  // Configure la broche de la LED en sortie
  pinMode(ledPin, OUTPUT);

  // On éteint la LED au démarrage (HIGH puisque active LOW)
  digitalWrite(ledPin, HIGH);

  // Initialise le Bridge (communication avec le cœur Linux)
  Bridge.begin();

  // Initialise le moniteur série côté STM32 (console dans App Lab)
  Monitor.begin();

  // Expose la fonction setLedState au cœur Linux.
  // Côté Python, on pourra appeler :
  //    bridge.call("setLedState", True)
  //    bridge.call("setLedState", False)
  Bridge.provide("setLedState", setLedState);

  Monitor.println("[C++] STM32 prêt, Bridge initialisé");
}

void loop() {
  // Pas de logique particulière côté STM32 :
  // tout est déclenché par les appels Bridge (setLedState)
  delay(10);
}
```
