#!/bin/bash

#LOGIN DATA
url="uptimekuma url" # Defaults to "https://status.muc.azubi.server.lan"
username="username"
password="password"
prox_host="proxmox-hostname" ## Defaults to oasis.muc.azubi.server.lan:443
prox_node="node" ## Defaults to "oasis"
prox_user="proxmox-username"
prox_pass="proxmox-password"
status="Backing up VM" # = Your MM Title (Status: Backing up VM 995)
stop_status="Stopping Backing up VM" # = Your MM Title (Status: Stopping Backing up VM 995)

echo "HOOK: $@"

# check for current "phase"
# input from proxmox example: backup-start stop 995
phase=$1
shift
stop=$1
shift
vmid=$1
shift

if [[ -z "$phase" || -z "$status" || -z "$vmid" ]]
then
    echo "HOOK: Nothing to do here $phase"
    exit 0
fi

phase=$(echo "$phase" | tr '[:upper:]' '[:lower:]')
status=$(echo "$status" | tr '[:upper:]' '[:lower:]')

# get vm hostname
hostname=${HOSTNAME}

# check if phase "job*" is active
if [[ "$phase" == 'pre-restart' ||
      "$phase" == 'post-restart' ||
      "$phase" == 'pre-start' ||
      "$phase" == 'post-start' ||
      "$phase" == 'pre-stop' ||
      "$phase" == 'job-init' ||
      "$phase" == 'job-start' ||
      "$phase" == 'stop' ||
      "$phase" == 'job-end' ||
      "$phase" == 'job-abort' ]]
then
    echo "HOOK: Nothing to do here $phase"
elif [[ "$phase" == 'backup-start' ]]
then
    # if backup is finished -> start maintenance mode
    echo "HOOK: Running $phase uptime.py (START)"
    sudo -u root python3 /root/uptime-api.py --vmid="$vmid" --phase='START' --status="$status" --"$stop_status" --url="$url"  -u="$username" -p="$password" --prox_host="$prox_host" --prox_node="$prox_node" --prox_user="$prox_user" --prox_pass="$prox_pass" || \
    echo "HOOK: Running uptime-api.py script at $phase failed" && exit 1
elif [[ "$phase" == 'backup-end' || "$phase" == 'backup-abort' ]]
then
    # if backup is finished -> stop maintenance mode
    echo "HOOK: Running $phase uptime.py (END)"
    sudo -u root python3 /root/uptime-api.py --vmid="$vmid" --phase='END' --status="$status" --"$stop_status" --url="$url"  -u="$username" -p="$password" --prox_host="$prox_host" --prox_node="$prox_node" --prox_user="$prox_user" --prox_pass="$prox_pass" || \
    echo "HOOK: Running uptime-api.py script at $phase failed" && exit 1
elif [[ "$phase" == 'log-end' ]]
then
    # if backup is finished wait until host is back online
    echo "HOOK: Running $phase uptime.py (LOG/WAIT)"
    sudo -u root python3 /root/uptime-api.py --vmid="$vmid" --phase='LOG-WAIT' --status="$status" --"$stop_status" --url="$url"  -u="$username" -p="$password" --prox_host="$prox_host" --prox_node="$prox_node" --prox_user="$prox_user" --prox_pass="$prox_pass" || \
    echo "HOOK: Running uptime-api.py script at $phase failed" && exit 1
else
    echo "HOOK: got unknown phase '$phase'"
fi
exit 0
