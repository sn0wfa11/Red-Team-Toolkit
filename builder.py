#!/usr/bin/env python2

try:
  import sys
  import argparse
  from lib.common import *
except Exception, err:
  import sys
  print >> sys.stderr, err
  sys.exit(1)

global verbose, dns_lookup, pattern

templates = []
numbers = []
pattern = "@{N}"
hosts = []
ips = []

def get_templates(filename):
  check_file(filename)
  with open(filename) as template_file:
    for line in template_file:
      line = line.strip()
      if line != "":
        templates.append(line)

def parse_args(args, parser):
  global verbose, dns_lookup, pattern

  verbose = args.verbose
  dns_lookup = args.dns_lookup

  if args.template_file:
    get_templates(args.template_file)

def main(argv):
  parser = argparse.ArgumentParser(description = "Create a list of host names from CDC host templates.")
  parser.add_argument("-T", "--template_file", type = str, help = "File containing host name templates. One per line.")
  parser.add_argument("-v", "--verbose", action = "store_true", help = "Verbose Reporting")
  parser.add_argument("-d", "--dns_lookup", action = "store_true", help = "Perform a DNS lookup and store IP address for each host.")
  parser.add_argument("range", type = str, 
  
  args = parser.parse_args()
  if len(argv) == 1:
    help_exit(parser)
  parse_args(args, parser)


if __name__ == "__main__":
  main(sys.argv)
