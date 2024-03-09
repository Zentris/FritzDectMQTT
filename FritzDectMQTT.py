# coding: utf8

# https://fritzconnection.readthedocs.io/en/1.13.2/sources/getting_started.html

# chrome-extension://gphandlahdpffmccakmbngmbjnjiiahp/https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA
# -HTTP-Interface.pdf


import os
import time

import yaml
import logging.config
from logging import Logger

#from fritzconnection import FritzConnection                        # TR-064
from fritzconnection.core.fritzconnection import FritzConnection    # HTML
from fritzconnection.core.exceptions import FritzServiceError, FritzHttpInterfaceError, FritzAuthorizationError

import MQTT


CONFIG_FILE_NAME_YAML = "configdata.cfg"
SECRETS_FILE_NAME_YAML = "secrets.yaml"

# --- Globals ---
configuration: dict
secrets: dict
logger: Logger

# ---------------
def abfrageFB(mqttCon):
    mqttData:dict = {}
    MAX_CONNECTION_TRYS = 10
    connectionerror = 0

    FB:dict = configuration["QUERY"]["FB"]
    fc: FritzConnection = None
    ain: str = ""

    try:
        while (fc is None and connectionerror < MAX_CONNECTION_TRYS):
            try:
                fc = FritzConnection(address=secrets["Fritzbox"][FB]["ip"],
                                     user=secrets["Fritzbox"][FB]["user"],
                                     password=secrets["Fritzbox"][FB]["password"],
                                     use_cache=True)
            except FritzAuthorizationError as fae:
                connectionerror += 1
                logger.debug("ConErrNo: {}, FritzAuthorizationError ('{}'".format(connectionerror, fae.args))

        result = fc.call_http("getswitchlist")
        switch_identifiers = result["content"].split(",")
        logger.info("Found list of AINs: {}".format(switch_identifiers))

        if configuration["QUERY"]["AINS"] == "ALL":
            selected_AINS = switch_identifiers
        else:
            selected_AINS = configuration["QUERY"]["AINS"]
            logger.debug("Use only pre-defined AINs {}".format(selected_AINS))

        try:
            for identifier in selected_AINS:
                ain = identifier.strip("\n")
                logger.info("Get AIN '{}'".format(ain))
                mqttData.update({"AIN": ain})

                result = fc.call_http("getswitchname", ain)
#                print(result)
                name:str = result["content"].strip("\n")
                mqttData["name"] = str(name)

                result = fc.call_http("gettemperature", ain)
#                print(result)
                t:str = result["content"].strip("\n")
                if t.isdigit():
                    temperature = float(t) / 10
                    mqttData["temp"] = temperature
                else:
                    mqttData["t-err"] = "NA"

                result = fc.call_http("getswitchpower", ain)
#                print(result)
                p: str = result["content"].strip("\n")
                if p.isdigit():
                    power = float(p) / 1000         # in Watt
                    mqttData["power"] = power
                else:
                    mqttData["p-err"] = "NA"

                logger.debug("AIN: {} Name: {} T: {}, P: {}".format(ain, name, t, p))
#                print(json.dumps(mqttData, indent=2, ensure_ascii=False))

                mqttCon.sendData(ain, mqttData)

        except FritzHttpInterfaceError as fbintexp:
            logger.error("AIN '{}' not exists on this FritzBox?".format(ain))
            logger.error(fbintexp.args)

    except FritzServiceError as fbexp:
        logger.error("Fehler: {}", fbexp.args)



# ---------------
def main(name):
    global configuration
    global secrets
    global logger

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
    logger = logging.getLogger("__main__")
    logger.info("------------Start program ------------")
    logger.info("Used Configfile: '{}'".format(CONFIG_FILE_NAME_YAML))

    mqtt = MQTT.MQTT(logger, configuration, secrets)
    mqtt.connection = mqtt.connect()

    while (True):
        looptime: int = 10

        with open(CONFIG_FILE_NAME_YAML, 'rt') as f:
            configuration = yaml.safe_load(f.read())

        abfrageFB(mqtt)

        if configuration["QUERY"]["looptime"] :
            looptime = configuration["QUERY"]["looptime"]

        time.sleep(looptime)


# ===================================
if __name__ == '__main__':
    main('PyCharm')


