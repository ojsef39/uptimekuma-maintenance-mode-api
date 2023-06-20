import argparse
import logging
import sys
import os
from uptime_kuma_api import UptimeKumaApi

#Maintenance mode will be abbreviated to MM
# e.g. search_maintenance_mode will be search_mm

def init():
    global api

    parser = argparse.ArgumentParser(prog='Uptime-API-Maintenance-mode',
                                     description='Python script to control '
                                                 'maintenance modes in uptime '
                                                 'kuma depending on Proxmox'
                                                 ' Backups')
    parser.add_argument('--log',
                        default='WARNING',
                        help="Set LogLevel DEBUG, INFO, WARNING, ERROR,"
                             " CRITICAL; If not set manually LogLevel "
                             "is set to WARNING by default")

    parser.add_argument('--host',
                        default=None,
                        help="Set host for which maintenance mode should be"
                             "activated/deactivated")

    args = parser.parse_args().__dict__
    log_level = args["log"].upper()
    mm_host = args["host"]

# Check if log_level is set
    if str(log_level) == "NOTHING" or log_level is None:
        log_level = "INFO"
    # Check if log_level is valid
    elif log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logging.critical(
            "LogLevel: " + str(log_level) +
            ' is not valid! Please enter NOTHING or a VALID option!'
            ' See example.env or docs!')
        sys.exit()

    # Set logging
    loglevel_err = getattr(logging, log_level)
    # Check if logging is accepting set log_level
    if not isinstance(loglevel_err, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # Display set log_level
    logging.info("LogLevel is set to: " + log_level)

    # Check if Host is set
    if mm_host == None:
        logging.critical("No maintenance mode host set… exiting")
        sys.exit()

    print("mm_host:" + mm_host) ##TODO: remove this after testing

    # Login to Uptime Kuma
    try:
        api = UptimeKumaApi(os.getenv("UPTIME_URL"))
        api.login(os.getenv('UPTIME_USER'), os.getenv("UPTIME_PASS"))
        # Login by token is not working for some reason?
        #api.login_by_token(os.getenv("UPTIME_TOKEN"))
        logging.debug("API INFO: " + str(api.info()))
    except:
        logging.error("There was an error while trying to login. Please try "
                      "again.")
        if log_level == "DEBUG":
            raise

def get_mm():
    mm_array = api.get_maintenances()
    for mm in mm_array:
        logging.debug("Found MM: ID: " + str(mm['id']) + ", Title: " + str(mm['title']) + ", Desc: " + str(mm['description']))
        parse_mm(mm['description'])

def parse_mm(description):
    # TODO: regex for "#description"
    print(description)

def main():
    init()
    get_mm()  # test function
    api.disconnect() # disconnect from api after use

if __name__ == '__main__':
    main()