# STILL WIP; DONT USE! #

### Python script to control maintenance modes in Uptime-Kuma ###
For feature requests or bugs/issues please create an [issue](https://gitlab.azubi.server.lan/lwsops-muc/uptimekuma-maintenance-mode-api/-/issues).

### Options: ###
#### Environmental: ####
see example.env

#### Parameters: ####

--log: "DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL". Defaults to "INFO"

--host: "Hostname". Used for matching a maintenance mode to a job/task/host. Kills script if not set.

--phase: "START", "END". Tells script to start or stop maintenance mode.

### Usage example: ###
In Proxmox the hostname of the VM thats currently is being backed up is "evergreen".

So the Proxmox hook (see ReadME in `use-with-proxmox` folders) calls the script `uptime-kuma-api.py --host="evergreen"` then
the script tries to match a maintenance mode to the given host.

To do this. Add `#hostname` so in this case `#evergreen` to the maintenance description.