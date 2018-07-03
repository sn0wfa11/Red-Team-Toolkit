import hashlib

def md5(data):
  return hashlib.md5(data).hexdigest()
