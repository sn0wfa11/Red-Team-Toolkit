#!/usr/bin/python

import sys

try:
  import argparse
  from lib.common import *
  from lib.logging import *
except Exception, err:
  print >> sys.stderr, err
  sys.exit(1)

global verbose, dns_lookup, pattern, numbers

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
        if pattern in line:
          templates.append(line)

def make_patterns():
  for number in numbers:
    for template in templates:
      hosts.append(template.replace(pattern, str(number)))

def build_range(in_string):
  output = []
  in_string = in_string.strip()
  sub_strings = in_string.split(",")

  for sub_string in sub_strings:
    dash_range = sub_string.split("-")
    if len(dash_range) == 1:
      output.append(int(sub_string))
    if len(dash_range) == 2:
      num_range = number_range(int(dash_range[0]), int(dash_range[1]))
      for num in num_range:
        output.append(num)

  return output 

def number_range(start, end):
  output = []
  if end < start:
    temp = start
    start = end
    end = temp

  for x in range(start, end + 1):
    output.append(x)
  return output  

def parse_args(args, parser):
  global verbose, dns_lookup, pattern, numbers

  verbose = args.verbose
  dns_lookup = args.dns_lookup

  if args.template:
    templates.append(args.template)
  if args.template_file:
    get_templates(args.template_file)
  if args.range:
    numbers = build_range(args.range)
  
def main(argv):
  parser = argparse.ArgumentParser(description = "Create a list of host names from CDC host templates.  The pattern to be replaced is \"@{N}\".  Example: www.team@{N}.isucdc.com")
  parser.add_argument("-T", "--template_file", type = str, help = "File containing host name templates. One per line.")
  parser.add_argument("-t", "--template", type = str, help = "Single template to parse")
  parser.add_argument("-v", "--verbose", action = "store_true", help = "Verbose Reporting")
  parser.add_argument("-d", "--dns_lookup", action = "store_true", help = "Perform a DNS lookup and store IP address for each host.")
  parser.add_argument("-r", "--range", type = str, help = "Ranges of team numbers. Example 1,3,5-10,12")
  parser.add_argument("-O", "--output_file", type = str, help = "File path to output the built results.")
  
  args = parser.parse_args()
  if len(argv) == 1:
    help_exit(parser)
  parse_args(args, parser)
  
  make_patterns()
  if args.output_file:
    write_list_to_file(args.output_file, hosts)
  else:
    for line in hosts:
      print line

if __name__ == "__main__":
  main(sys.argv)
