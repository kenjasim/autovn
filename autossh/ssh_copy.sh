#!/usr/bin/expect

# Login variables 
set hostname [lindex $argv 0]
set hostaddr [lindex $argv 1]
set password [lindex $argv 2]
set keyapath [lindex $argv 3]

puts "Sending SSH RSA key to $hostname@$hostaddr..."
sleep 1

# create SSH session with host 
eval spawn ssh-copy-id -f -i $keyapath $hostname@$hostaddr
# await password request 
expect "password"
# Send password
send "$password\r"
expect eof
