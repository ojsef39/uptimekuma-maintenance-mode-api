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
    parser.add_argument('--status',
                        default="Backing up VM",
                        help="Set backup status.")
    parser.add_argument('-u',
                        '--username',
                        default=None,
                        help="Set uptime username (In the future token login will be possible)")
    parser.add_argument('-p',
                        '--password',
                        default=None,
                        help="Set uptime password (In the future token login will be possible)")
    parser.add_argument('--url',
                        default="https://status.muc.azubi.server.lan")


    args = parser.parse_args().__dict__
    log_level = args["log"].upper()
    global mm_vmid
    mm_vmid = args["vmid"]
    global mm_phase
    mm_phase = args["phase"]
    global mm_status
    mm_status = args["status"]
    global uptime_user
    uptime_user = args["username"]
    global uptime_pass
    uptime_pass = args["password"]
    global uptime_url
    uptime_url = args["url"]

# Check if log_level is set
    if str(log_level) == "NOTHING" or log_level is None:
        log_level = "INFO"
    # Check if log_level is valid
    elif log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logging.critical(
            "LogLevel: " + str(log_level) +
            ' is not valid! Please enter NOTHING or a VALID option!'
            ' See docs for help!')
        sys.exit()

    # Check if log_level is set
    if mm_phase is not None:
        mm_phase = mm_phase.upper()
    if mm_phase not in ["START", "END", "LOG-WAIT"]:
        logging.critical(
            'Phase was not set correctly!'
            ' See docs for help!')
        sys.exit()

    # Set logging
    loglevel_err = getattr(logging, log_level)
    # Check if logging is accepting set log_level
    if not isinstance(loglevel_err, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # Display set log_level
    #logging.info("START OF LOG")
    logging.info("LogLevel is set to: " + log_level)

    # Check if Host is set
    if mm_vmid is None:
        logging.critical("No maintenance mode host set… exiting...")
        sys.exit()

    # Login to Uptime Kuma
    if log_level == "DEBUG":
        ssl_verify = False
    else:
        ssl_verify = True

    try:
        api = UptimeKumaApi(uptime_url, ssl_verify=ssl_verify)
        api.login(uptime_user, uptime_pass)
        # Login by token is not working for some reason?
        #api.login_by_token(os.getenv("UPTIME_TOKEN"))
        logging.debug("API INFO: " + str(api.info()))
    except:
        logging.error("There was an error while trying to login."
                      " For more help check readME ")
        raise
        sys.exit()

def get_mm():
    mm_array = api.get_maintenances()
    # log maintenances and run parse
    for mm in mm_array:
        logging.debug("Found MM: ID: " + str(mm['id']) + ", Title: " +
                      str(mm['title']) + ", Desc: " + str(mm['description']))
        parse_mm(mm['id'], mm['description'], mm['title'])

def parse_mm(mm_id, mm_description, mm_title):
    # match "#example" and "#ex-ample"
    match_tag = re.findall(r"#([\w-]+)", mm_description)
    match_tag = re.findall(r"#([\w-]+)", mm_description)
    #get only last match
    for tag in match_tag:
        change_mm(tag, mm_id, mm_title)

def change_mm(last_match, mm_id, mm_title):
    if last_match == mm_vmid:
        if mm_phase == "START":
            api.resume_maintenance(mm_id)
            change_mm_title(mm_id, mm_title)
            print("HOOK: Resumed maintenance mode ID: " + str(mm_id)
                  + " Name: " + mm_title)
        elif mm_phase == "END":
            api.pause_maintenance(mm_id)
            change_mm_title(mm_id, mm_title)
            print("HOOK: Pausing maintenance mode ID: " + str(mm_id)
                  + " Name: " + mm_title)

def change_mm_title(mm_id, mm_title):
    if mm_phase == "START":
        status_start_index = mm_title.find("(Status:")  # Find the index of "(Status:"
        if status_start_index != -1:
            mm_title = mm_title[:status_start_index]
        changed_title = mm_title +  " (Status: " + mm_status + " " + mm_vmid + ")"
        api.edit_maintenance(mm_id,
                             title=changed_title)
        logging.debug("Changed MM Title to: " + changed_title)
    elif mm_phase == "END":
        status_start_index = mm_title.find("(Status:")  # Find the index of "(Status:"
        if status_start_index != -1:
            changed_title = mm_title[:status_start_index]
            api.edit_maintenance(mm_id,
                                 title=changed_title)
            logging.debug("Changed MM Title from " + mm_title +  " to: " + changed_title)


def main():
    init()
    get_mm()  # test function
    api.disconnect() # disconnect from api after use
    logging.debug("Script finished, api disconnected, END OF LOG!")

if __name__ == '__main__':
    main()