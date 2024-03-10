# FritzDectMQTT
Das Script liest per Http-API aus einer Fritzbox die Daten der dort angeschlossenen DECT-Steckdosen aus.
**Geplant** ist auch das Auslesen weiterer Geräte (Heizungsregler, Rollläden)

Diese Daten werden dann an einen **MQTT Broker** versendet. Dieser muss eingerichtet und per Netzwerk erreichbar sein.

Das Script ist primär für die Verwendung auf einem Raspberian Microrechner (RasPi) konzipiert. Es kann natürlich auf jedem 
anderen Linuxrechner mit installiertem Python 3.10 oder höher verwendet werden.

Die Konfigurationsscripte sind für den Standard-RasPi-User `pi` eingerichtet, ein abweichender Username ist dort entsprechen zu 
korrigieren. 

---
## Einrichtungsschritte
  * Das File `_secrets.yaml` mit den passenden Fritzbox-Zugangsdaten versehen.
  * Das File `_secrets.yaml` muss dann nach `secrets.yaml` umbenannt werden.
  * Einrichten eines [Virtuellen Environment für Python](#Python-Virtuelles-Environment-(venv)-einrichten)
  * Einrichten der [Logfile-Rotation](#Logfile-Rotation)
  * Einrichten eines [Systemdienstes zum automatischen Starten](#Service-(systemctl)) 

### Python Virtuelles Environment (venv) einrichten
Ein Virtual Environment bietet die Möglichkeit, mehrere parallele Instanzen des Python-Interpreters aufzusetzen, wobei jede 
mit unterschiedlichen Packages und Konfigurationen ausgestattet werden kann. Jede virtuelle Umgebung enthält eine eigenständige Kopie des Python-Interpreters, einschließlich Kopien der unterstützenden Dienstprogramme.

    # Python virtual environent installieren
    sudo apt-get install python3-venv

    # gehe in das Projektverzeichnis
    cd ~/FritzDectMQTT

    # Virtuelles environment initialisieren
    python -m venv ~/FritzDectMQTT/venv

    # Einbinden des venv in die aktuelle Sitzungsumgebung
    source ~/FritzDectMQTT/venv/bin/activate

    # Installieren der für das Projekt notwendigen Python Module
    pip install -r requirements.txt

Der Pfad in der `fritzdectmqtt.service` - Datei muss entsprechend dem Usernamen angepasst werden.

---

### Logfile-Rotation
Um zu vermeiden, dass das Filesystem des Rechners durch die Logfiles voll läuft, wird die Logrotate Funktionalität des 
Linux-OS verwendet.

Falls ``logrotate`` noch nicht installiert ist, installiere es:

    sudo apt install logrotate

Kopiere das File ``fritzdectmqtt.logrotate``:

    sudo cp cli/fritzdectmqtt.logrotate /etc/logrotate.d/fritzdectmqtt 

---

### Service (systemctl)
Das Script läuft permanent, die Abrufen-Abstände der Fritzbox-Werte werden über **looptime** gesteuert (``configdata.cfg``)

###### -- Umkopieren --

    sudo cp cli/fritzdectmqtt.service /etc/systemd/system

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





