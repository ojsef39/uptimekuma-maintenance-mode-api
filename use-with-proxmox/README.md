# Usage of script-runner-uptime-api.pl: #

1. `mkdir /var/lib/vz/snippets`
2. `cp /path/to/script-runner-uptime-api.pl /var/lib/vz/snippets/`
3. `chmod +x /var/lib/vz/snippets/script-runner-uptime-api.pl`
4. customize it to your needs -> `$username`, `$password`, `$status` 

Add `script /var/lib/vz/snippets/script-runner-uptime-api.pl` to `/etc/pve/jobs.cfg` like this:
````
vzdump: backup-########-####
schedule sun 01:00
compress zstd
enabled 1
mailnotification always
mode stop
node oasis
notes-template {{guestname}}
script /var/lib/vz/snippets/script-runner-uptime-api.pl
storage backups
vmid 995`
````
You can test if the hook works with (you need a maintenance with #995 in the description):

`/var/lib/vz/snippets/script-runner-uptime-api.pl backup-start/end stop 995`

### Please note: ###

The hook runs following command: `python3 /root/uptime-api.py --vmid=$vmid --phase='START/END' --status=$status -u=$username' -p=$password'"`, so 
please ensure the `uptime-api.py` can be found in `/root/uptime-api.py`
