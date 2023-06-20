#!/usr/bin/perl -w

use strict;

print "HOOK: " . join (' ', @ARGV) . "\n";
# check for current "phase"
my $phase = shift;
# check if phase "job*" is active
if ($phase eq 'job-init' ||
$phase eq 'job-start' ||
$phase eq 'job-end' ||
$phase eq 'job-abort') {

#if ($phase eq 'job-start') {
#system ("/bin/sh /root/uptime-api.sh") == 0 ||
#die "Running uptime-api.sh script at job-start failed";
#}

#if ($phase eq 'job-end') {
#system ("/bin/sh /root/uptime-api.sh") == 0 ||
#die "Running uptime-api.sh script at job-end failed";
}

# check if phase "backup*" is active
} elsif ($phase eq 'backup-start' ||
$phase eq 'backup-end' ||
$phase eq 'backup-abort' ||
$phase eq 'log-end' ||
$phase eq 'pre-stop' ||
$phase eq 'pre-restart' ||
$phase eq 'post-restart') {

# if backup is starting -> start maintenance mode
if ($phase eq 'backup-start') {
system ("/bin/sh /root/uptime-api.sh --host=$host --phase='START'") == 0 ||
die "Running uptime-api.sh script at backup-start failed";
}
# if backup is finished -> stop maintenance mode
if ($phase eq 'backup-end') {
system ("/bin/sh /root/uptime-api.sh --host=$host --phase='END'") == 0 ||
die "Running uptime-api.sh script at backup-end failed";
}

} else {

die "got unknown phase '$phase'";

}

exit (0);