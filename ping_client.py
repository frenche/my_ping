#!/usr/bin/python
import argparse, sys, socket, string

class Ping:
    def __init__(self, proto, target, port, timeout, size):
      self.proto = proto
      self.target = target
      self.port = port
      self.timeout = timeout
      self.data = (string.ascii_letters *
                    (size/len(string.ascii_letters) +1))[:size]

    def send(self):
        if self.proto == 'tcp':
          return self.send_tcp()
        if self.proto == 'udp':
          return self.send_udp()

        raise BaseException('unknown protocol')

    def send_udp(self):
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.settimeout(self.timeout)

      if sock.sendto(self.data, (self.target, self.port)) != len(self.data):
        raise BaseException('send_udp: failed to send all data')

      if self.data != sock.recv(len(self.data)):
        raise BaseException('send_udp: failed to receive all data')

      return True

    def send_tcp(self):
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.settimeout(self.timeout)
      sock.connect((self.target, self.port))

      if sock.send(self.data) != len(self.data):
        raise BaseException('send_tcp: failed to send all data')

      sock.shutdown(socket.SHUT_WR)

      if self.data != sock.recv(len(self.data)):
        raise BaseException('send_tcp: failed to receive all data')

      return True


def parse_args():
  parser = argparse.ArgumentParser(description='Ping client over TCP/UDP')
  parser.add_argument('target', default = 'localhost', help = "Target host")
  parser.add_argument('--count', default = '4', type=int, help = "Number of ping request")
  parser.add_argument('--protocol', default='udp', help = "Protocol to use")
  parser.add_argument('--port', default = 5555, type=int, help = "Port to use")
  parser.add_argument('--timeout', default = 15, type=int, help = "Port to use")
  parser.add_argument('--size', default = 32, type=int, help = "The size of data")

  return vars(parser.parse_args())

if __name__ == '__main__':
  args = parse_args()

  ping = Ping(args['protocol'], args['target'], args['port'], args['timeout'], args['size'])
  for i in range(args['count']):
    print "Ping number ", i, ": Ok" if ping.send() else ": Failed"
