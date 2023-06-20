#!/usr/bin/perl -w

use strict;
print "HOOK: " . join (' ', @ARGV) . "\n";
# check for current "phase"
my $vmid = shift;
my $phase = shift;
$phase = lc($phase);
# get vm hostname
my $hostname = $ENV{HOSTNAME};
# check if phase "job*" is active
if ($phase eq 'job-init' || $phase eq 'job-start' || $phase eq 'backup-start' ||$phase eq 'pre-restart' || $phase eq 'post-restart') {

    # if backup is starting -> start maintenance mode
    print("Running uptime.py (START)\n");
    system ("python3 /root/uptime-api.py --vmid=$vmid --phase='START'") == 0 ||
    die "Running uptime-api.py script at backup-start failed";

} elsif ($phase eq 'backup-end' || $phase eq 'job-end' || $phase eq 'job-abort' || $phase eq 'backup-abort' || $phase eq 'log-end' || $phase eq 'pre-stop') {

    # if backup is finished -> stop maintenance mode
    print("Running uptime.py (END)\n");
    system ("python3 /root/uptime-api.py --vmid=$vmid --phase='END'") == 0 ||
    die "Running uptime-api.py script at backup-end failed";

} else {

    die "got unknown phase '$phase'";
    }
exit (0);