#!/usr/bin/perl -w

use strict;
#LOGIN DATA
my $username = "username";
my $password = "password";
my $override = "override";
#print "HOOK: " . join (' ', @ARGV) . "\n";
# check for current "phase"
#TODO:Use of uninitialized value $phase in string eq at ./use-with-proxmox/script-runner-uptime-api.pl line 12. when only one arg is given (phase=vmid)
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
if ($phase eq 'pre-restart' ||
$phase eq 'post-restart' ||
$phase eq 'log-end') {
    print "HOOK: Nothing to do here $phase\n";

} elsif ($phase eq 'pre-start' || $phase eq 'post-start' || $phase eq 'backup-start') {

    # if backup is finished -> start maintenance mode
    print("HOOK: Running $phase uptime.py (START)\n");
    system ("python3 /root/uptime-api.py --vmid=$vmid --phase='START' -u=$username -p=$password") == 0 ||
    die "HOOK: Running uptime-api.py script at backup-start failed\n";

} elsif ($phase eq 'pre-stop' || $phase eq 'backup-end' || $phase eq 'backup-abort') {

    # if backup is finished -> stop maintenance mode
    print("HOOK: Running $phase uptime.py (END)\n");
    system ("python3 /root/uptime-api.py --vmid=$vmid --phase='END' -u=$username -p=$password") == 0 ||
    die "HOOK: Running uptime-api.py script at backup-stop/end/abort failed\n";

} elsif ($phase eq 'job-init' || $phase eq 'job-start') {
    if ($override ne "override" && $phase eq $vmid) {
        # if backup is starting -> start maintenance mode
        print("HOOK: Running $phase uptime.py (START)\n");
        system ("python3 /root/uptime-api.py --vmid=$override --phase='START' -u=$username -p=$password") == 0 ||
        die "HOOK: Running uptime-api.py script at job-init/start failed\n";
    }

} elsif ($phase eq 'stop' || $phase eq 'job-end' || $phase eq 'job-abort') {
    if ($override ne "override" && $phase eq $vmid) {
        # if backup is finished -> stop maintenance mode
        print("HOOK: Running $phase uptime.py (END)\n");
        system ("python3 /root/uptime-api.py --vmid=$override --phase='END' -u=$username -p=$password") == 0 ||
        die "HOOK: Running uptime-api.py script at job-end/abort/stop failed\n";
    }

} else {

    die "HOOK: got unknown phase or override enabled $vmid '$phase'\n";
}
exit (0);