#!/usr/bin/expect

# Login variables 
set hostname [lindex $argv 0]
set hostaddr [lindex $argv 1]
set password [lindex $argv 2]
set keyapath [lindex $argv 3]
set lineterminationChar "\r"

puts "Sending SSH RSA key to $hostname@$hostaddr..."
sleep 1

# create SSH session with host 
eval spawn ssh-copy-id -f -i $keyapath $hostname@$hostaddr

# handle fingerprint OR password request 
expect {
        # handle new fingerprint request 
        "fingerprint" {send "yes\r"}
        # handle password request (preempts if fingerprint not requested) 
        "password" {send "$password\r"; puts "Password sent 1."}
        # Host is already known and auth not required 
        eof {puts "Host is known, password authentication not requested."}
    }

# handle password request IF fingerprint request in previous expect 
# check spawn has not closed/completed 
catch {
        expect {
                "password" {send "$password\r"; puts "\nPassword sent 2."}
                timeout {puts "Password not requested."}
            }
        expect eof
} err_result

# Print to console 
# puts $output
# puts $err_result 


        

