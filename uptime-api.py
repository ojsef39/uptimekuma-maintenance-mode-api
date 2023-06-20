import argparse
import logging
import re
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

    parser.add_argument('--vmid',
                        default=None,
                        help="Set vmid for which maintenance mode should be"
                             "activated/deactivated")
    parser.add_argument('--phase',
                        default=None,
                        help="Set phase to start or stop maintenance mode.")

    args = parser.parse_args().__dict__
    log_level = args["log"].upper()
    global mm_vmid
    mm_vmid = args["vmid"]
    print("vmid: " + mm_vmid)
    global mm_phase
    mm_phase = args["phase"]

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

    # Check if log_level is set
    if mm_phase is not None:
        mm_phase = mm_phase.upper()
    if mm_phase not in ["START", "END"]:
        logging.critical(
            'Phase was not set correctly!'
            ' See example.env or docs!')
        sys.exit()

    # Set logging
    loglevel_err = getattr(logging, log_level)
    # Check if logging is accepting set log_level
    if not isinstance(loglevel_err, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(filename='uptime-api.log',
                        filemode='a',
                        level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # Display set log_level
    logging.info("START OF LOG")
    logging.info("LogLevel is set to: " + log_level)

    # Check if Host is set
    if mm_vmid is None:
        logging.critical("No maintenance mode host set… exiting")
        sys.exit()

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
        sys.exit()

def get_mm():
    mm_array = api.get_maintenances()
    # log maintenances and run parse
    for mm in mm_array:
        logging.debug("Found MM: ID: " + str(mm['id']) + ", Title: " +
                      str(mm['title']) + ", Desc: " + str(mm['description']))
        parse_mm(mm['id'], mm['description'], mm['title'])

def parse_mm(mm_id, mm_description, title):
    # match "#example" and "#ex-ample"
    matches = re.findall(r"#([\w-]+)", mm_description)
    #get only last match
    if matches:
        last_match = matches[-1]
        change_mm(last_match, mm_id, title)
    else:
        logging.critical("No match found exiting…")

def change_mm(last_match, mm_id, title):
    if last_match == mm_vmid:
        if mm_phase == "START":
            api.resume_maintenance(mm_id)
            logging.info("Resumed maintenance mode ID: " + str(mm_id)
                         + " Name: " + title)
        elif mm_phase == "END":
            api.pause_maintenance(mm_id)
            logging.info("Pausing maintenance mode ID: " + str(mm_id)
                         + " Name: " + title)
    else:
        logging.critical("Last match: " + last_match + " is not matching: "
                     + mm_vmid + ". Exiting…")

def main():
    init()
    get_mm()  # test function
    api.disconnect() # disconnect from api after use
    logging.debug("Script finished, api disconnected, END OF LOG!")

if __name__ == '__main__':
    main()