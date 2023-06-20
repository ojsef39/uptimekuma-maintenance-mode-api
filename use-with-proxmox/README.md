# Usage of script-runner-uptime-api.pl: #

1. `mkdir /var/lib/vz/snippets`
2. `cp /path/to/script-runner-uptime-api.pl /var/lib/vz/snippets/`
3. `chmod +x /var/lib/vz/snippets/script-runner-uptime-api.pl`

Now set following command in proxmox for every VM/CT you want to run this script for:

`qm set 100 --hookscript local:snippets/script-runner-uptime-api.pl` (100 = VMID)