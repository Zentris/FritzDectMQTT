# FritzDectMQTT
Das Script liest per http-API aus einer Fritzbox die Daten der dort angeschlossenen DECT-Steckdosen aus.

Diese Daten werden dann an einen MQTT Broker versendet.

Das Script ist primär für die Verwendung auf einem Raspberian Microrechner konzipiert. Es kann natürlich auf jedem anderen 
Linuxrechner mit installiertem Python 3.10 oder höher verwendet werden.

---
## Einrichtung
  * Vor Verwendung muss das File ``_secrets.yaml`` mit den passenden Zugangsdaten versehen werden.
  * Das File ``_secrets.yaml`` muss dann nach ``secrets.yaml`` umbenannt werden.
  * Ein MQTT Broker muss eingerichtet und erreichbar sein.

### Logfile-Rotation
Um zu vermeiden, dass das Filesystem des Rechners durch die Logfiles voll läuft, wird die Logrotate Funktionalität des 
Linux-OS verwendet.

Falls ``logrotate`` noch nicht installiert ist, installiere es:

    sudo apt install logrotate

Kopiere das File ``fritzdectmqtt.logrotate``:

    sudo cp cli/fritzdectmqtt.logrotate /etc/logrotate.d/fritzdectmqtt 

### Service (systemctl)
Das Script läuft permanent, die Abrufen-Abstände der Fritzbox-Werte werden über **looptime** gesteuert (``configdata.cfg``)

###### -- Aktivieren --

    sudo systemctl enable fritzdectmqtt.service

###### -- Starten --

    sudo systemctl start fritzdectmqtt.service

###### -- Kontrolle -- 

    sudo systemctl status fritzdectmqtt.service

###### -- Stoppen --

    sudo systemctl stop fritzdectmqtt.service

---

*Das Projekt ist in einer frühen Phase, die Fehlererkennung ist noch in einer relativ rudimentären Qualität.*





