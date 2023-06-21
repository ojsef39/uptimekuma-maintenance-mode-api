# STILL WIP; BUT IT SHOULD WORK #
**Use branch `master`!** Default branch is `dev`
### Python script to control maintenance modes in Uptime-Kuma ###
For feature requests or bugs/issues please create an [issue](https://gitlab.azubi.server.lan/lwsops-muc/uptimekuma-maintenance-mode-api/-/issues).

Logs are created in the file `uptime-api.log` in the same directory as the script

Requirements (at least until built version is available):
- `pip install uptime_kuma_api`

### Options: ###

`--log`: "DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL". Defaults to "INFO"

`--vmid`: "vmid". Used for matching a maintenance mode to a job/task/host/vmid. Kills script if not set.

`--phase`: "START", "END". Tells script to start or stop maintenance mode.

`--status`: Set backup status e.g. "Backing up VM" for "Your VM Title (Status: Backing up VM `#995`"

`-u`, `--username`: "Uptime Kuma Username"

`-p`, `--password`: "Uptime Kuma Password (Token login will be added in future)"

`--url`: "https://url.to.statuspage/" Defaults to: "https://status.muc.azubi.server.lan"

### Usage example: ###
In Proxmox the hostname of the VM thats currently is being backed up is "evergreen" with the VMID 995.

So the Proxmox hook (see ReadME in `use-with-proxmox` folder) calls the script `python3 /root/uptime-api.py --vmid=$vmid --phase='START/END' --status=$status -u=$username' -p=$password'"` then
the script tries to match a maintenance mode to the given tag (`#995`). 

Every MM with the specified tag in the description will be activated.
So the Proxmox hook (see ReadME in `use-with-proxmox` folder) calls the script `python3 /root/uptime-api.py --vmid=$vmid --phase='START/END' -u=$username' -p=$password'"` then
the script tries to match a maintenance mode to the given tag (`#995`).

To do this. Add `#vmid` so in this case `#995` to the maintenance description.

For single Maintenance mode use eg. for a backup schedule, you can use overwrite (see ReadME in `use-with-proxmox` folder)