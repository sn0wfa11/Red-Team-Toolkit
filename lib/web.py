import socket
import urllib

def nslookup(host):
  try:
    ip = socket.gethostbyname(host)
  except:
    return ""
  return ip

def url_encode(in_str):
  return urllib.quote_plue(in_str)

def nx_url_encode(in_str):
  return url_encode(in_str).replace("%0D", "")
