#!/usr/bin/env python2

# This is 
#
#
# by sn0wfa11

import sys

try:
  import socket
  import subprocess
  import os
  import argparse
except Exception, err:
  print >> sys.stderr, err
  sys.exit(1)

global host, start, end, command, verbose

command = "/bin/bash"
verbose = False

# Argument parser
def parse_args(args, parser):
  global host, start, end, command, verbose
  verbose = args.verbose
  

  if args.delay:
    delay = args.delay

  if args.host:
    split_host_port(args.host)
  if args.host_file:
    get_hosts(args.host_file)
  if len(hosts) < 1:
    print_exit("You must specify at least one host!", parser)

  if args.username:
    usernames.append(args.username)
  if args.user_file:
    get_usernames(args.user_file)
  if len(usernames) < 1:
    print_exit("You must specify at least one username!", parser)

  if args.password:
    passwords.append(args.password)
  if args.pass_file:
    get_passwords(args.pass_file)
  if len(passwords) < 1:
    print_exit("You must specify at least one password!", parser)

  if args.command:
    commands.append(args.command)
  if args.command_file:
    get_commands(args.command_file)

# Main Function
def main(argv):
  parser = argparse.ArgumentParser(description = "Brute Forcer for SSH with ability to execute commands and check for sudo rights.")
  parser.add_argument("-u", "--username", type = str, help = "Single username to test")
  parser.add_argument("-U", "--user_file", type = str, help = "File containing usernames. One per line.")
  parser.add_argument("-p", "--password", type = str, help = "Single password to test")
  parser.add_argument("-P", "--pass_file", type = str, help = "File containing passwords. One per line.")
  parser.add_argument("-t", "--host", type = str, help = "Single host to test. <host> or <host>:<port> IPv6 is ok too.")
  parser.add_argument("-T", "--host_file", type = str, help = "File containing hosts. One per line. <host> or <host>:<port> IPv6 is ok too.")
  parser.add_argument("-v", "--verbose", action = "store_true", help = "Display all host:username:password tests.")
  parser.add_argument("-w", "--pairwise", action = "store_true", help = "Test username and password combos in line by line match. Must have same number of each!")
  parser.add_argument("-d", "--delay", type = int, choices = [1, 2, 3, 4, 5, 6, 7, 8], help = "Delay amout. Increase in case of errors. Default = 4")
  parser.add_argument("-s", "--screen_root", action = "store_true", help = "Spawn an ssh login in screen for root credentials only.")
  parser.add_argument("-S", "--screen", action = "store_true", help = "Spawn an ssh login in screen for all found credentials.")
  parser.add_argument("-c", "--command", type = str, help = "Single command to run on successful ssh login.")
  parser.add_argument("-C", "--command_file", type = str, help = "File containing commands to run on successful ssh login. One per line.")
  parser.add_argument("-r", "--root_cmd", action = "store_true", help = "Only run specified command on login when root or sudo account found.")
  parser.add_argument("-D", "--sudo_check", action = "store_true", help = "Check for sudo rights on non-root logins.")
  
  args = parser.parse_args()
  if len(argv) == 1:
    help_exit(parser)
  parse_args(args, parser)

  print_status("Starting brute force...")

  run_hosts()
  print_status("Done.")

# Ref to main function
if __name__ == "__main__":
  try:
    main(sys.argv)
  except KeyboardInterrupt:
    print "\n\n[*] Exiting..."
    sys.exit(3)
