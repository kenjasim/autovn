#!/usr/bin/expect

# Login variables 
set hostname [lindex $argv 0]
set hostaddr [lindex $argv 1]
set password [lindex $argv 2]

puts "Starting SSH session with $hostname@$hostaddr..."
sleep 1

# create SSH session with host 
eval spawn ssh -oStrictHostKeyChecking=no -oCheckHostIP=no $hostname@$hostaddr

# Use the correct prompt
set prompt ":|#|\\\$"
interact -o -nobuffer -re $prompt return # wait for prompt and return 
# wait for password request (consider if problems, other requests may preempt) 
expect "password"
# Send password
send "$password\r"
interact -o -nobuffer -re $prompt return

# Send a single command
# send "ls\r"
# interact -o -nobuffer -re $prompt return
# interact -o -nobuffer -re "(.*)\\r" return # wait for any output and return

# Run interactive shell 
interact

# RESOURCES
# https://stackoverflow.com/questions/4780893/use-expect-in-a-bash-script-to-provide-a-password-to-an-ssh-command
# https://www.mkssoftware.com/docs/man1/expect.1.asp

# osascript -e "tell application \"Terminal\" to do script \"cd /directory/to/open && /path/to/command command\""
# osascript -e "tell application \"Terminal\" to do script \"cd ~/Documents/Code && ./ssh_connect.sh dev 20.0.0.5 ved \""
