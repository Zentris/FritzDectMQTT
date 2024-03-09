
import os
import logging.config
import json, yaml
import time
import paho.mqtt.client as mqttClient

class MQTT:
    """

    """

    MQTTClient: mqttClient

    # -------------------
    def __init__(self, Logger: logging = None, ConfigData: dict = None, SecretData: dict = None):
        """
        """
        assert (ConfigData is not None), "No config data given"
        assert (SecretData is not None), "No secret data given"

        self.mqttConfData = ConfigData["MQTT"]
        self.mqttSecData = SecretData["MQTT_BROKER"]["RASPI_PH"]
        self.fritzbox: str = ConfigData["QUERY"]["FB"]

        self.logger = logging.getLogger(__name__)

    # -------------------
    def connect(self) -> mqttClient:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker ")
            else:
                print("Failed to connect to MQTT Broker, return code %d\n".format(rc))

        def on_disconnect(client, userdata, rc):
            FIRST_RECONNECT_DELAY = 1
            RECONNECT_RATE = 2
            MAX_RECONNECT_COUNT = 12
            MAX_RECONNECT_DELAY = 60

            self.logger.warning("Disconnected with result code: %s", rc)
            reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
            while reconnect_count < MAX_RECONNECT_COUNT:
                self.logger.warning("Reconnecting in %d seconds...", reconnect_delay)
                time.sleep(reconnect_delay)

                try:
                    client.reconnect()
                    self.logger.info("Reconnected successfully!")
                    return
                except Exception as err:
                    self.logger.error("%s. Reconnect failed. Retrying...", err)

                reconnect_delay *= RECONNECT_RATE
                reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
                reconnect_count += 1
            self.logger.warning("Reconnect failed after %s attempts. Exiting...", reconnect_count)


        self.MQTTClient = mqttClient.Client(mqttClient.CallbackAPIVersion.VERSION1, self.mqttConfData["clientId"])
#        if self.secretData["user"] is not None and self.secretData["password"] is not None:
#            self.MQTTClient.username_pw_set(self.secretData["user"], self.secretData["password"])

        self.MQTTClient.on_connect = on_connect
        self.MQTTClient.on_disconnect = on_disconnect

        try:
            retCode = self.MQTTClient.connect(str(self.mqttSecData["ip"]), int(self.mqttSecData["port"]))

            if mqttClient.MQTTErrorCode.MQTT_ERR_SUCCESS == retCode:
                self.logger.info("Connection successfull")
            else:
                self.logger.error("Connect Broker {}:{} not successfull (retCode='{}'), no exception given"
                              .format(self.mqttSecData["ip"], self.mqttSecData["port"], retCode))
        except Exception as err:
            self.logger.error("Connection error: {}".format(err.args))

        # if self.MQTTClient.is_connected():
        #     self.logger.info("Connect Broker {}:{} successfull"
        #                      .format(self.mqttSecData["ip"], self.mqttSecData["port"]))
        # else:
        #     self.logger.error("Connect Broker {}:{} not successfull, no exception given"
        #                       .format(self.mqttSecData["ip"], self.mqttSecData["port"]))

        return self.MQTTClient

    # -----------------
    def sendData(self, addTopic: str = "", sendData: dict = None):
        assert (sendData is not None), "No data to send given"

        currentTopic = self.mqttConfData["maintoken"] + "/" + self.fritzbox + "/" + addTopic

        self.logger.debug("Current topic: '{}'".format(currentTopic))

        sendString = json.dumps(sendData, ensure_ascii=False)
        result = self.MQTTClient.publish(currentTopic, sendString)

        if result[0] == 0:
            self.logger.info("Send '{}' to {}:{} with topic '{}'".format(sendString, self.mqttSecData["ip"],
                                                                         self.mqttSecData["port"],
                                                                         currentTopic))
        else:
            self.logger.error("Failed to send message to topic '{}'".format(currentTopic))


# ======================================
if __name__ == '__main__':
    CONFIG_FILE_NAME_YAML = "configdata.cfg"
    SECRETS_FILE_NAME_YAML= "secrets.yaml"

    if not os.path.exists(CONFIG_FILE_NAME_YAML):
        raise NameError("Config file '{}' is not accessible.".format(CONFIG_FILE_NAME_YAML))
    with open(CONFIG_FILE_NAME_YAML, 'rt') as f:
        configuration = yaml.safe_load(f.read())

    if not os.path.exists(SECRETS_FILE_NAME_YAML):
        raise NameError("Config file '{}' is not accessible.".format(SECRETS_FILE_NAME_YAML))
    with open(SECRETS_FILE_NAME_YAML, 'rt') as f:
        secrets = yaml.safe_load(f.read())

    if "logging" not in configuration:
        raise Exception("No logging configuration in configuration file '{}' available.".format(CONFIG_FILE_NAME_YAML))

    logging.config.dictConfig(configuration["logging"])
    logger = logging.getLogger("MQTT")
    logger.info("------------Start MQTT Test ------------")
    logger.info("Used Configfile: '{}'".format(CONFIG_FILE_NAME_YAML))

    testdata = {
       "116570433098" : {
           "AIN": "116570433098",
           "name": "Au\u00dfenStkd. Garage: Wasserpumpe",
           "temp": 6.5,
           "power": 0.0
       },
       "116570387991" : {
          "AIN": "116570387991",
          "name": "Leuchtb\u00e4umchen vor Haust\u00fcr",
          "temp": 13.5,
          "power": 4.28
       }
    }

#    mqtt = MQTT(logger, configuration, secrets, "FB_Moehlau")
#    mqtt.connect()

    for ain in testdata.keys():
#        mqtt.sendData(addTopic=ain, sendData=testdata[ain])
        print("name: {}".format(testdata[ain]["name"]))
        print(testdata[ain]["name"])


