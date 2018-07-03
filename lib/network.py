import socket

# Check if the target port is open on the host
def port_open(host, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(2)
  result = sock.connect_ex((host,port))
  sock.close()
  if result == 0:
    return True
  else:
    return False
