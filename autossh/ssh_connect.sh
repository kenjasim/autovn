#!/usr/bin/expect

# Login variables 
set hostname [lindex $argv 0]
set hostaddr [lindex $argv 1]
set password [lindex $argv 2]
set hostport [lindex $argv 3]

puts "Starting SSH session with $hostname@$hostaddr..."
sleep 1

# create SSH session with host 
eval spawn ssh -oStrictHostKeyChecking=no -oCheckHostIP=no $hostname@$hostaddr -p $hostport

# Use the correct prompt
set prompt ":|#|\\\$"

# handle password request (consider if problems, other requests may preempt) 
expect {
        # handle password request (preempts if fingerprint not requested) 
        "password" {send "$password\r"; puts "\nPassword sent."}
    }

# Run interactive shell 
interact


################################################################################
# Resources
################################################################################

# https://stackoverflow.com/questions/4780893/use-expect-in-a-bash-script-to-provide-a-password-to-an-ssh-command
# https://www.mkssoftware.com/docs/man1/expect.1.asp