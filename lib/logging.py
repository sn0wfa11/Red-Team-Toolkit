def write_list_to_file(filepath, in_list):
  try:
    out_file = open(filepath, "w+")
    for line in in_list:
      out_file.write(line + "\n")
    out_file.close()
  except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))

def apend_list_to_file(filepath, in_list):
  try:
    out_file = open(filepath, "a+")
    for line in in_list:
      out_file.write(line + "\n")
    out_file.close()
  except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))
