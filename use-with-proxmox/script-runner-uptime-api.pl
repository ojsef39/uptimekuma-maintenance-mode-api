#!/usr/bin/perl -w

use strict;
#LOGIN DATA
my $username = "username";
my $password = "password";
my $status = "Backing up VM"; # = Your MM Title (Status: Backing up VM 995)
print "HOOK: " . join (' ', @ARGV) . "\n";
# check for current "phase"
#TODO:Use of uninitialized value $phase in string eq at ./use-with-proxmox/script-runner-uptime-api.pl line 12. when only one arg is given (phase=vmid)
#backup-start stop 995
my $phase = shift;
my $stop = shift;
my $vmid = shift;
unless (defined $phase && defined $status && defined $vmid) {
    print "HOOK: Nothing to do here $phase\n";
    exit(0)
}
$phase = lc($phase);
$status = lc($status);
# get vm hostname
my $hostname = $ENV{HOSTNAME};
# check if phase "job*" is active
if ($phase eq 'pre-restart' ||
$phase eq 'post-restart' ||
$phase eq 'log-end') {
    print "HOOK: Nothing to do here $phase\n";

} elsif ($phase eq 'pre-start' || $phase eq 'post-start' || $phase eq 'backup-start' || $phase eq 'pre-stop') {

    # if backup is finished -> start maintenance mode
    print("HOOK: Running $phase uptime.py (START)\n");
    ## TOOD: Find out which user runs this so its ensured uptime_kuma_api is installed
    system ("sudo -u root python3 /root/uptime-api.py --vmid=$vmid --phase='START' --status=$status -u=$username -p=$password") == 0 ||
    die "HOOK: Running uptime-api.py script at $phase failed\n";

} elsif ($phase eq 'backup-end' || $phase eq 'backup-abort') {

    # if backup is finished -> stop maintenance mode
    print("HOOK: Running $phase uptime.py (END)\n");
    ## TOOD: Find out which user runs this so its ensured uptime_kuma_api is installed
    system ("sudo -u root python3 /root/uptime-api.py --vmid=$vmid --phase='END' --status=$status -u=$username -p=$password") == 0 ||
    die "HOOK: Running uptime-api.py script at $phase failed\n";

} else {

    print "HOOK: got unknown phase '$phase'\n";
}
exit (0);