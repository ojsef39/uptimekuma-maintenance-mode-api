## STILL WIP; BUT IT SHOULD WORK ##

***Use branch `master`! Default branch is `dev`***
### Python script to control maintenance modes in Uptime-Kuma ###
For feature requests or bugs/issues please create an [GitHub Issues](https://github.com/ojsef39/uptimekuma-maintenance-mode-api).

Logs are created in the file `uptime-api.log` in the same directory as the script

Requirements:
- `pip install uptime_kuma_api`

Update Script:
- `sudo ./prepare.sh`

### Options: ###

`--log`: "DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL". Defaults to "INFO"

`--vmid`: "vmid". Used for matching a maintenance mode to a job/task/host/vmid. Kills script if not set.

`--phase`: "START", "END". Tells script to start or stop maintenance mode.

`--status`: Set backup status e.g. "Backing up VM" for "Your VM Title (Status: Backing up VM `#995`"

`--url`: "https://url.to.statuspage/" Defaults to: "https://status.muc.azubi.server.lan"

`-u`, `--username`: "Uptime Kuma Username"

`-p`, `--password`: "Uptime Kuma Password (Token login will be added in future)"

If using with proxmox hook:

`--prox_host`: "Proxmox URL"

`--node`: "Proxmox Node"

`--prox_user`: "Proxmox User"

`--prox_pass`: "Proxmox Password"

### Usage example: ###
In Proxmox the hostname of the VM thats currently is being backed up is "evergreen" with the VMID 995.

So the Proxmox hook (see ReadME in `use-with-proxmox` folder) calls the script `python3 /root/uptime-api.py --vmid="$vmid" --phase='END' --status="$status" --"$stop_status" --url="$url"  -u="$username" -p="$password" --prox_host="$prox_host" --prox_node="$prox_node" --prox_user="$prox_user" --prox_pass="$prox_pass"'` then
the script tries to match a maintenance mode to the given tag (`#995`). 

Every MM with the specified tag in the description will be activated.

To do this. Add `#vmid` so in this case `#995` to the maintenance description.