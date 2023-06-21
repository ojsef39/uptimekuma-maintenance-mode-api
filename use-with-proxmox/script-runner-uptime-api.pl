#!/usr/bin/perl -w

use strict;
print "HOOK: " . join (' ', @ARGV) . "\n";
# check for current "phase"
my $vmid = shift;
my $phase = shift;
# if $phase is
if ($phase eq '') {
    $phase = $vmid;
}
$phase = lc($phase);
# get vm hostname
my $hostname = $ENV{HOSTNAME};
# check if phase "job*" is active
if ($phase eq 'backup-start' ||
$phase eq 'pre-start' ||
$phase eq 'pre-restart' ||
$phase eq 'post-restart' ||
$phase eq 'pre-stop' ||
$phase eq 'stop' ||
$phase eq 'backup-end' ||
$phase eq 'backup-abort' ||
$phase eq 'log-end') {
    print "HOOK: Nothing to do here";

} elsif ($phase eq 'job-init' || $phase eq 'job-start') {

    # if backup is starting -> start maintenance mode
    print("HOOK: Running uptime.py (START)\n");
    system ("sudo python3 /root/uptime-api.py --vmid=$vmid --phase='START'") == 0 ||
    die "HOOK: Running uptime-api.py script at backup-start failed";

} elsif ($phase eq 'job-end' || $phase eq 'job-abort') {

    # if backup is finished -> stop maintenance mode
    print("HOOK: Running uptime.py (END)\n");
    system ("sudo python3 /root/uptime-api.py --vmid=$vmid --phase='END'") == 0 ||
    die "HOOK: Running uptime-api.py script at backup-end failed";

} else {

    die "HOOK: got unknown phase '$phase'";
    }
exit (0);