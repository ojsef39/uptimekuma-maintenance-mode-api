# STILL WIP; USE WITH CAUTION BUT IT SHOULD WORK #
**Use branch `master`!** Default branch is `dev`
### Python script to control maintenance modes in Uptime-Kuma ###
For feature requests or bugs/issues please create an [issue](https://gitlab.azubi.server.lan/lwsops-muc/uptimekuma-maintenance-mode-api/-/issues).

Logs are created in the file `uptime-api.log` in the same directory as the script

### Options: ###
#### Environmental: ####
see example.env

#### Parameters: ####

--log: "DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL". Defaults to "INFO"

--vmid: "vmid". Used for matching a maintenance mode to a job/task/host/vmid. Kills script if not set.

--phase: "START", "END". Tells script to start or stop maintenance mode.

### Usage example: ###
In Proxmox the hostname of the VM thats currently is being backed up is "evergreen".

So the Proxmox hook (see ReadME in `use-with-proxmox` folder) calls the script `python3 uptime-kuma-api.py --vmid="995" --phase="start"` then
the script tries to match a maintenance mode to the given host.

To do this. Add `#vmid` so in this case `#995` to the maintenance description.