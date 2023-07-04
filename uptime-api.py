# Copyright 2023 Josef Hofer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import os
import re
import sys
import time
from uptime_kuma_api import UptimeKumaApi
from proxmoxer import ProxmoxAPI

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
    parser.add_argument('--stop_status',
                        default="Finished/Aborted Backing up VM",
                        help="Set backup status on stop/end/abort.")
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
    parser.add_argument('--prox_host',
                        default="oasis.muc.azubi.server.lan:443")
    parser.add_argument('--node',
                        default="oasis"),
    parser.add_argument('--prox_user',
                        default=None)
    parser.add_argument('--prox_pass',
                        default=None)


    args = parser.parse_args().__dict__
    log_level = args["log"].upper()
    global mm_vmid
    mm_vmid = args["vmid"]
    global mm_phase
    mm_phase = args["phase"]
    global mm_status
    mm_status = args["status"]
    global mm_stop_status
    mm_stop_status = args["stop_status"]
    global uptime_user
    uptime_user = args["username"]
    global uptime_pass
    uptime_pass = args["password"]
    global uptime_url
    uptime_url = args["url"]
    global prox_host
    prox_host = args["prox_host"]
    global node
    node = args["node"]
    global prox_user
    prox_user = args["prox_user"]
    global prox_pass
    prox_pass = args["prox_pass"]

    global hostname
    hostname = None
    global ip_address
    ip_address = None

# Check if log_level is set
    if str(log_level) == "NOTHING" or log_level is None:
        log_level = "INFO"
    # Check if log_level is valid
    elif log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logging.warning(
            "LogLevel: " + str(log_level) +
            ' is not valid! Please enter NOTHING or a VALID option!'
            ' See docs for help!')
        exit(0)

    # Check if log_level is set
    if mm_phase is not None:
        mm_phase = mm_phase.upper()
    if mm_phase not in ["START", "END", "LOG-WAIT"]:
        logging.warning(
            'Phase was not set correctly!'
            ' See docs for help!')
        exit(0)

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
    logging.debug("VMID is set to: " + str(mm_vmid))

    # Check if Host is set
    if mm_vmid is None:
        logging.warning("No maintenance mode host set… exiting...")
        exit(0)

    # Disable SSL verification if log_level is DEBUG
    if log_level == "DEBUG":
        ssl_verify = False
    else:
        ssl_verify = True
    
    # Login to Uptime Kuma
    try:
        api = UptimeKumaApi(url=uptime_url, ssl_verify=ssl_verify)
        api.login(uptime_user, uptime_pass)
        # Login by token is not working for some reason?
        #api.login_by_token(os.getenv("UPTIME_TOKEN"))
        logging.debug("API INFO: " + str(api.info()))
    except:
        logging.error("There was an error while trying to login."
                      " For more help check readME ")
        # raise  # uncomment to see full error
        exit(0)

# Use proxmox api to bin vmid to hostnames and ips
def bind_mm_to_host_and_ip():

    try:
        prox_api = ProxmoxAPI(
            prox_host, user=prox_user, password=prox_pass, verify_ssl=False
        )

        # Get ip from hostname
        try:
            # Try qemu first, if it fails try lxc
            vm = prox_api.nodes(node).qemu(mm_vmid)
            network_interfaces = vm.agent('network-get-interfaces').get()
            if network_interfaces is not None:
                for statistics in network_interfaces["result"]:
                    for ip_configs in statistics["ip-addresses"]:
                        if ip_configs["ip-address-type"] == "ipv4" and ip_configs["ip-address"] != "127.0.0.1":
                            ip_address = (ip_configs["ip-address"])
                            print("HOOK: IP found (PVEAPI): " + str(ip_address))
                            break
        except:
            try:
                vm = prox_api.nodes(node).lxc(mm_vmid).config.get()
                if vm is not None:
                    for config in vm:
                        if config == "net0":
                            net_config = vm[config]
                            for item in net_config.split(','):
                                if item.startswith('ip='):
                                    ip_address = item[3:] # Remove ip=
                                    ip_address = ip_address.split('/')[0] # Remove subnet
                                    print("HOOK: IP found (PVEAPI): " + str(ip_address))
                                    break
                
                else:
                    logging.warning("No ip found for vmid: " + str(mm_vmid))
                    exit(0)
            except:
                ip_address = None
                logging.warning("Something went wrong getting ip of: " + str(mm_vmid))
                raise

        # Get hostname from vmid
        try:
            vm = prox_api.nodes(node).qemu(mm_vmid).config.get()
        except:
            vm = prox_api.nodes(node).lxc(mm_vmid).config.get()
        try:
            if vm is not None:
                try:
                    hostname = vm["name"]
                except KeyError:
                    hostname = vm["hostname"]
                print("HOOK: Hostname found (PVEAPI): " + str(hostname))
            else:
                logging.error("No hostname found for vmid: " + str(mm_vmid))
                exit(0)
        except:
            logging.warning("Something went wrong getting hostname of: " + str(mm_vmid))
            exit(0)

    except:
        logging.warning("There was an error while using proxmox api.")
        #raise ## uncomment to see full error

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
            mm_start(mm_id, mm_title)
        elif mm_phase == "END":
            mm_end(mm_id, mm_title)
            
        elif mm_phase == "LOG-WAIT":
            mm_log_wait(mm_id, mm_title)            

def mm_start(mm_id, mm_title):
    logging.debug("Start maintenance mode for: " + str(mm_id))
    api.resume_maintenance(mm_id)
    change_mm_start(mm_id, mm_title)
    print("HOOK: Resumed maintenance mode ID: " + str(mm_id)
            + " Name: " + mm_title)

def mm_end(mm_id, mm_title):
    logging.debug("End maintenance mode for: " + str(mm_id))
    api.resume_maintenance(mm_id)
    change_mm_end(mm_id, mm_title)
    print("HOOK: Resumed (end) maintenance mode ID: " + str(mm_id)
            + " Name: " + mm_title)

def mm_log_wait(mm_id, mm_title):
    logging.debug("Log wait for: " + str(mm_id))
    api.resume_maintenance(mm_id)
    change_mm_log_wait(mm_id, mm_title)
    api.pause_maintenance(mm_id)
    print("HOOK: Paused (log-wait) maintenance mode ID: " + str(mm_id))

def clear_mm_title(mm_id, mm_title):
    
    status_start_index = mm_title.find("(Status:")  # Find the index of "(Status:"
    if status_start_index != -1:
        mm_title = mm_title[:status_start_index]
    changed_title = mm_title
    api.edit_maintenance(mm_id,
                            title=changed_title)
    logging.debug("Changed MM Title to: " + changed_title)

def change_mm_start(mm_id, mm_title):
    status_start_index = mm_title.find("(Status:")  # Find the index of "(Status:"
    if status_start_index != -1:
        mm_title = mm_title[:status_start_index]
    if hostname is None:
        changed_title = mm_title +  " (Status: " + str(mm_status) + " " + str(mm_vmid) + ")"
    else:
        changed_title = mm_title +  " (Status: " + str(mm_status) + " " + str(hostname) + ")"
    api.edit_maintenance(mm_id,
                        title=changed_title)
    logging.debug("Changed MM Title to: " + changed_title)

def change_mm_end(mm_id, mm_title):
    status_start_index = mm_title.find("(Status:")  # Find the index of "(Status:"
    if status_start_index != -1:
        mm_title = mm_title[:status_start_index]
    if hostname is None:
        changed_title = mm_title +  " (Status: " + str(mm_stop_status) + " " + str(mm_vmid) + ")"
    else:
        changed_title = mm_title +  " (Status: " + str(mm_stop_status) + " " + str(hostname) + ")"
    api.edit_maintenance(mm_id,
                            title=changed_title)
    logging.debug("Changed MM Title from " + mm_title +  " to: " + changed_title)

def change_mm_log_wait(mm_id, mm_title):
    ## Show that its waiting for the host to be up again
    status_start_index = mm_title.find("(Status:")  # Find the index of "(Status:"
    if status_start_index != -1:
        mm_title = mm_title[:status_start_index]
    if hostname is None:
        changed_title = mm_title +  " (Status: Waiting for " + str(mm_vmid) + ")"
    else:
        changed_title = mm_title +  " (Status: Waiting for " + str(hostname) + ")"
    api.edit_maintenance(mm_id,
                            title=changed_title)
    logging.debug("Changed MM Title from " + mm_title +  " to: " + changed_title)
    logging.debug("Waiting for host to be up again...")
    is_host_up()
    ## Host is up again, end maintenance mode
    clear_mm_title(mm_id, mm_title)

def is_host_up():
    ## When ip is "dhcp", do nothing

    if ip_address is None:
        print("HOOK: IP is not set, host may be offline")
        return False
    elif ip_address is not None and ip_address != "dhcp":

        logging.debug("Checking if host is up in 2 seconds...")
        time.sleep(2)
        # ping host 10 times until back online
        check_count = 1
        while True:
            response = os.system("ping -c 1 " + str(ip_address) + " > /dev/null 2>&1")
            if check_count <= 10:
                if response == 0:
                    print("HOOK: Host is up again, ending maintenance mode...")
                    return True
                else:
                    logging.debug("( " + str(check_count) + ") Host is still down, waiting two seconds and then trying again...")
                    time.sleep(2)
                    check_count += 1
            else:
                print("HOOK: Host is still down after 10 checks, something went wrong...")
                return False
    else:
        print("HOOK: IP is dhcp or not set, not checking if host is up again...")
        return False


def main():
    init()
    bind_mm_to_host_and_ip()
    get_mm()
    api.disconnect() # disconnect from api after use
    logging.debug("Script finished, api disconnected, END OF LOG!")

if __name__ == '__main__':
    main()
