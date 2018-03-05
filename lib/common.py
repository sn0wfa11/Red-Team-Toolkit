import os
import sys

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  GOOD = '\033[92m'
  WARNING = '\033[93m'
  ERROR = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


# Printing With Colors Functions
def print_good(text):
  print bcolors.GOOD + "[*]" + bcolors.ENDC + " " + text

def print_nomatch(text):
  print bcolors.ERROR + "[*]" + bcolors.ENDC + " " + text

def print_error(text):
  print bcolors.ERROR + "\n[*] " + text + bcolors.ENDC + "\n"

def print_status(text):
  print "[*] " + text

def printv_good(text, verbose):
  if verbose:
    print bcolors.GOOD + "[*]" + bcolors.ENDC + " " + text

def printv_nomatch(text, verbose):
  if verbose:
    print bcolors.ERROR + "[*]" + bcolors.ENDC + " " + text

def printv_error(text, verbose):
  if verbose:
    print bcolors.ERROR + "\n[*] " + text + bcolors.ENDC + "\n"

def printv_status(text, verbose):
  if verbose:
    print "[*] " + text

# Input File Checking
def check_file(filename):
  if os.path.exists(filename) == False:
    print "\n[*] File " + filename + " Does Not Exist!"
    sys.exit(4)

# Show parser help and exit
def help_exit(parser):
  parser.print_help()
  sys.exit(1)

# Print a message, show parser help and exit
def print_exit(message, parser):
  print_error(message)
  parser.print_help()
  sys.exit(1)

