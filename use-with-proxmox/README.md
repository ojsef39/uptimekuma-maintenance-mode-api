# Usage of script-runner-uptime-api.pl: #

1. `mkdir /var/lib/vz/snippets`
2. `cp /path/to/script-runner-uptime-api.pl /var/lib/vz/snippets/`
3. `chmod +x /var/lib/vz/snippets/script-runner-uptime-api.pl`
4. customize it to your needs -> `$username`, `$password`

Now set following command in proxmox for every VM/CT you want to run this script for:

`/usr/sbin/qm set 995 --hookscript local:snippets/script-runner-uptime-api.pl` (995 = VMID)

Check if hook is set:

`/usr/sbin/qm config 995`

You can test if the hook works with (you need a maintenance with #995 in the description):

`HOSTNAME=test /var/lib/vz/snippets/script-runner-uptime-api.pl backup-start/end`

### Overwrite Option (Single Maintenance Panel with single backup schedule)
Because there is no option to match a scheduled backup to a mm panel i built in this option:

1. follow the 4 steps from above
2. edit `$overwrite` to the tag you have in you panel description eg. `$overwrite="panel"` with tag `#panel`

Unfortunately you can then only set one panel and one backup schedule

### Please note: ###

The hook runs following command: `python3 /root/uptime-api.py --vmid=$vmid --phase='START/END' -u=$username' -p=$password'"`, so 
please ensure the `uptime-api.py` can be found in `/root/uptime-api.py`