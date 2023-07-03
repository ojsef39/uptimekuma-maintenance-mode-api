# Usage of script-runner-uptime-api.pl: #

1. `sudo ./prepare.sh --proxmox` (pulls and moves files to the right place)
2. `chmod +x /var/lib/vz/snippets/script-runner-uptime-api.sh`
3. customize values in script to your needs -> `$username`, `$password`, `$status`, `$stop_status`, `$prox_host`, `$prox_user`, `$prox_pass`

##TODO: Add qm set thing back when it should work for single backups too
Add `script /var/lib/vz/snippets/script-runner-uptime-api.sh` to `/etc/pve/jobs.cfg` like this:
````
vzdump: backup-########-####
schedule sun 01:00
compress zstd
enabled 1
mailnotification always
mode stop
node oasis
notes-template {{guestname}}
script /var/lib/vz/snippets/script-runner-uptime-api.sh
storage backups
vmid 995`
````
You can test if the hook works with (you need a maintenance with #995 in the description):

`/var/lib/vz/snippets/script-runner-uptime-api.pl backup-start/end stop 995`

### Please note: ###

The hook runs following command: `python3 /root/uptime-api.py --vmid="$vmid" --phase='END' --status="$status" --"$stop_status" --url="$url"  -u="$username" -p="$password" --prox_host="$prox_host" --prox_node="$prox_node" --prox_user="$prox_user" --prox_pass="$prox_pass"'"`, so 
please ensure the `uptime-api.py` can be found in `/root/uptime-api.py`
