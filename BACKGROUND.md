# Background Information

## Terminology
HRU = Heat Recovery Unit
WRG = Wärmerückgewinnungsgerät

Control Modules = Control Units (LED or TFT) + External Inputs (Boost Ventilation and Fan Speed)
Steuerungsmodule = Bedieneinheit (LED oder TFT) + Externe Eingänge (Stosslüftung und Lüfterstufen)

Zu- und Abluft Modus
Supply air and extract air mode

Ventilation -> Fan Speed (FS0-FS3)
Lüfter -> Lüfterstufen (LS0-LS3)

Un-occupied mode
Abwesend-Modus

Automatic mode (timing mode or sensor mode)
Automatik-Modus (Zeitautomatik oder Sensorautomatik)

Messages
Meldungen

## Basic Information

### Paul Novus Interfaces

|Platine|Name|Ader|Paar|Kontaktbezeichnung|Notiz|
|:----|:----|:----|:----|:----|:----|
|X10|Durchgangsklemme|1|Statusrelais|Schliesser Statusrelais (max. 24 V Schaltspannung)| |
|X10|Durchgangsklemme|2|Statusrelais|Wechsler Statusrelais (max. 24 V Schaltspannung)| |
|X10|Durchgangsklemme|3|Stosslüftungstaster|Ader 1| |
|X10|Durchgangsklemme|4|Stosslüftungstaster|Ader 2 (GND)| |
|X10|Durchgangsklemme|5|Externe Freigaber (Brücke)|Externe Freigabe|Brücke Set. If removed, TFT Blocked, LED L1+L7 Blink|
|X10|Durchgangsklemme|6|Externe Freigaber (Brücke)|Externe Freigabe (GND)| |
|X10|Durchgangsklemme|7|Digitale Ein- und Ausgänge|DIO1 (Automatik-Modus aktivieren)| |
|X10|Durchgangsklemme|8|Digitale Ein- und Ausgänge|DIO1 (GND)| |
|X10|Durchgangsklemme|9|Externer Sensor - Analog Eingang|Ader 1 (Sensorsignal 0-10V oder 4-20 mA)| |
|X10|Durchgangsklemme|10|Externer Sensor - Analog Eingang|Ader 2 (GND)| |
|X1|RS485 BUS|1| |Rot - 24P|TBC|
|X1|RS485 BUS|2| |Weiss - RX| |
|X1|RS485 BUS|3| |Gelb - TX| |
|X1|RS485 BUS|4| |Schwarz - GND| |
|X1|RS485 BUS|5| |Alufarben - Schirm| |
|X2| |7| | |TBC|
|X2| |6| | |TBC|

### Own System

|Geräte Typ|NOVUS300|
|:----|:----|
|Ausführung|L-VER-DEF (Vertical Left)|
|Production Date|14/03/2017|
|S/N|741929834|
|Slave Board HW-Version|10430|
|TFT SKU|CU-TFT-NOV300-450RD|
|TFT S/N|521014140|
|Bus-Version|1.7.1|
|Master Version|SWZ0024B31A|
|Slave Version|SWZ0025B27A|
|Defroster|ST00064E26E|
|ControlUnit1|ETA0035E20A|
|ControlUnit2|ETA0036E31E|
|ControlUnit3|---|
|Angeschlossene Geräter|Master (X), Bedieneinheit (X), Lüfter-Slave (X), Defroster (X), Heizregister (), EWT-Klappe ()|

### Error Codes

|Fehlermeldung|Mögliche Ursache|Kontrolle / Massnahme|Code|More|Code bis|
|:----|:----|:----|:----|:----|:----|
|Sensorfehler Sensor 1|Sensorbruch oder Kurzschluss. Temperaturfühler T1 (L) / T3 (R)|Fühler prüfen bzw. Sensor erneuern|81 ??| | |
|Sensorfehler Sensor 2|Sensorbruch oder Kurzschluss. Temperaturfühler T2 (L) / T4 (R)|Fühler prüfen bzw. Sensor erneuern|82 ??| | |
|Sensorfehler Sensor 3|Sensorbruch oder Kurzschluss. Temperaturfühler T3 (L) / T1 (R)|Fühler prüfen bzw. Sensor erneuern|83 ??| | |
|Sensorfehler Sensor 4|Sensorbruch oder Kurzschluss. Temperaturfühler T4 (L) / T2 (R)|Fühler prüfen bzw. Sensor erneuern|84 ??| | |
|Zulufttemperatur zu niederig|minimale Zulufttemperatur < Sollwert|Zulufttemperatur > Sollwert + 1 K|85 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20| | |
|Aussentemperatur zu niederig|aktuelle Aussenlufttemperatur < Sollwert; länger als 30 min|Aussenlufttemperatur > Sollwert; Kontrolle nach 1 h|86 ??| | |
|Fehler Lüfter 1 Hall|Zuluftlüfter (L) / Fortluftlüfter (R) meldet keine Drehzahl|manuelles Einstellen einer Lüfterstufe|87 ??| | |
|Fehler Lüfter 2 Hall|Fortluftlüfter (L) / Zuluftlüfter (R) meldet keine Drehzahl|manuelles Einstellen einer Lüfterstufe|88 ??| | |
|Fehler Bypass|Keine Endlagenposition, Bypass defekt|Bypass testen|89 4f 75 74 20 6f 66 20 72 61 6e 67 65 20 20 20|Out of Range|89 4f 75 74 20 6f 66 20 72 61 6e 67 65 20 20 20|
|BUS Version inkompatibel|Software-Versionen der Komponenten nicht kompatibel|Software-Versionen austauschen|c0 ??| | |
|Zu viele Geräte angeschl.|Zu viele Komponenten am BUS angeschlossen|Überzahlige Komponenten entfernen|c1 ??| | |
|Lüfterslave nicht angeschl.|Fehlende BUS-Kommunikation|Lüfterslave anschliessen|c2 ??| | |
|Kommunikationsfehler Lüfterslave|Fehlende BUS-Kommunikation|BUS-Kommunikation überprüfen|c3 ??| | |
|Komm.-fehler Defroster|Fehlende BUS-Kommunikation|BUS-Kommunikation überprüfen|c7 44 65 66 72 6f 73 74 65 72 20 20 20 20 20 20| | |
|Komm.-fehler Heizregister|Fehlende BUS-Kommunikation|BUS-Kommunikation überprüfen|c5 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20| | |
|Komm.-fehler EWT-Klappe|Fehlende BUS-Kommunikation|BUS-Kommunikation überprüfen|c6 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20| | |
|Komm.-fehler allgemein|BUS-Komponenten der Steuerung werden nicht erkannt|Netztrennung, denach Neustart|c4 ??| | |
|Heizung schaltet nicht ab|Fehler BUS-Thermostat|BUS-Thermostat auswechseln|c8 ??| | |
|Allgemeiner BDE Fehler|Fehlende BUS-Kommunikation mit Bedieneinheit (BDE)|BUS-Kommunikation überprüfen|c9 ??| | |

#### LED Display

|L1|L2|L3|L4|L5|L6|L7|L8|L9|L10|L11|L12|Fehlermeldung|Mögliche Ursache|
|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|
|X| |X| | | | | | | | | |Zulufttemperatur zu niedrig|minimale Zulufttemperatur < Sollwert|
|X| | |X| | | | | | | | |Fehler Bypass|Keine Endlagenposition, Bypass defekt|
|X|X| |X|X| |X| | | | | |BUS Version inkompatibel|Software-Versionen der Komponenten nicht kompatibel|
| | |X|X|X| |X| | | | | |Zu viele Geräte angeschlossen|Zu viele Komponenten am BUS angeschlossen|
|X| |X|X|X| |X| | | | | |Lüfterslave nicht angeschlossen|Fehlende BUS-Kommunikation|
| |X|X|X|X| |X| | | | | |Kommunikationsfehler Lüfterslave|Fehlende BUS-Kommunikation|
|X|X|X|X|X| |X| | | | | |Kommunikationsfehler Defroster|Fehlende BUS-Kommunikation|
| | | | | |X|X| | | | | |Kommunikationsfehler Heizregister|Fehlende BUS-Kommunikation|
|X| | | | |X|X| | | | | |Kommunikationsfehler EWT-Klappe|Fehlende BUS-Kommunikation|
| |X| | | |X|X| | | | | |Kommunikationsfehler allgemein|Fehlende BUS-Kommunikation|
|X|X| | | |X|X| | | | | |Heizung schaltet nicht ab|Fehler BUS-Thermostat|
| |X| |X|X| | | | | | | |Allgemeiner BDE Fehler|Fehlende BUS-Kommunikation mit Bedieneinheit (BDE)|
|X| | | | | |X| | | | | |Keine externe Freigabe: Lüfter aus| |
| | | | | | | |X| | | | |Blinken; Fehler Sensor: Ventilatoren werden abgeschaltet, Bypass schliesst| |
| | | | | | | |X| | |X|X|Blinken; Allgemeiner Fehler, die Fehlernummer wird binär mit den LEDs L1 bis L7 dargestellt| |
| | | | | | | | | | |X| |Blinken; Fehler Lüfter 1 Hall: Ventilatoren werden abgeschaltet, Bypass schliesst.| |
| | | | | | | | | | | |X|Blinken; Fehler Lüfter 2 Hall: Ventilatoren werden abgeschaltet, Bypass schliesst.| |

### Lüfterstufen
|Stufe|Lüfter Sollwertvorgabe (%)|
|:----|:----|
|0|0|
|1|17|
|2|29|
|3|41|
|4|53|
|5|65|
|6|74|
|7|100|

## Reverse Engineering

### Boot Sequence

Master sends out a register request to all devices (on each address 01 02 to 01 0C - 01 01 is the Master). Command 80 (including the Bus Version)
If no slave is answering to this request within 160ms, the Master sends out the same request again (same message)
If a slave is answering to the registration request, it does this with Command 81 (including the Bus Version, Device Type(?) and Device HW/SW Version)
The master acknowledges the slave registration with a Command 81 without any data (this happens 50ms after the registration request)
Registrations are closed approx. 160ms after last REQ_REQ (on last slave address) by sending Command 83 (is this command a request to dump Memory?). Now accepting Command 85
Master sends now approx. each 100ms an ALIVE message (Command 84) to each registered slave.
Master also sends approx. each 9s an ALIVE message to (Command 84) to FF (asking for new available devices?)

Devices ask if there are any Mem changes (Cmd86). Master answers with Cmd87 and the Checksum as data. Some addresses require Confirmation (Cmd87), others dont (Pings or Status like Fanspeed, Temperatures)
If a Cmd85 is sent (to Memory?! = 0x00) then each device acknowledges the retrival (each device 0x01--) with a Cmd86. The Master commits then the Cmd85 to the device using a Cmd87 with the Checksum from Cmd85 as Data

Devices ask if Master still alive with (Cmd84). Master asnwers with Cmd85 (this write is not confirmed with Cmd87)

### Notes

If VMC crash/reset, then following addresses are reset to default: 3d, 5a, 3e, 3f, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 4a, 4b (in a single Cmd85)

if VMC crash/reset, then there is no "REGISTRATION", just a REGISTARTION CLOSE (01 00 83)

if VMC crash/reset, acknowledge (Cmd87) with checksum 00 00

Is Cmd88 --> Error? Seems to occur when Writing with Cmd85 and Acknowledge (Cmd87) with inexisting Checksum as Data


IMPORTANT: sending smth with Cmd85 doesn't require manuel Cmd86 or Cmd87


### To be done

FIGURE OUT: Bridged (TFT locked) // External Release
FIGURE OUT: Type of Device (Novus 300/450 // Novus F 300/450)
FIGURE OUT: Construction Type: Vertical, Horizontal Left, Vertical, Horizontal Right Version
FIGURE OUT: Digital Output active (via programming)
FIGURE OUT: Register for Filter Change "NOW" or not?

Find MAR for:
- t_aut (Aussentemperatur) / t_out Outside temperature	T5
- t_sde (Eintrittstemperatur Sole-Defroster) / t_bde inlet temperature brine defroster	T6
- t_nhz (Austrittstemperatur Nachheizregister) / t_shb outlet temperature supply heater battery	T7
- t_rth (Temperatur am Raumthermostat) / t_rth temperature of the termostat	T8