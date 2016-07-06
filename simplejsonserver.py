from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import csv
import json
 
class LocalData(object):
  records = []
  max_val = 0
  def __init__(self):
    self.records = []
    with open('airports.csv', 'rb') as csvfile:
        airportreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        airportreader.next()
        for row in airportreader:
            self.records.append({'Aiport': row[0].strip(), 'Paxes': row[1].strip()})
            
    self.max_val = len(self.records)
    LocalData.max_val = len(self.records)
    LocalData.records = self.records
    
class HTTPRequestHandler(BaseHTTPRequestHandler):
  def do_POST(self):
    print "execute do_POST", self.path

    self.send_response(403)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    return
 
  def do_GET(self):
    print "execute do_GET", self.path
    if None != re.search('/api/v1/getpaxes/*', self.path):
      try:
        recordID = int(self.path.split('/')[-1])
      except ValueError:
        self.send_response(400, 'Bad Request: parameter incorrect')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        return
        
      if recordID > 0 and recordID <= LocalData.max_val:
        paxes_list = json.dumps(LocalData.records[:recordID-1])
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(paxes_list)
      else:
        self.send_response(400, 'Bad Request: parameter too large')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
    else:
      self.send_response(403)
      self.send_header('Content-Type', 'application/json')
      self.end_headers()
    return
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  allow_reuse_address = True
 
  def shutdown(self):
    self.socket.close()
    HTTPServer.shutdown(self)
 
class SimpleHttpServer():
  def __init__(self, ip, port):
    self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
 
  def start(self):
    self.server_thread = threading.Thread(target=self.server.serve_forever)
    self.server_thread.daemon = True
    self.server_thread.start()
 
  def waitForThread(self):
    self.server_thread.join()
 
  def stop(self):
    self.server.shutdown()
    self.waitForThread()
 
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='HTTP Server')
  parser.add_argument('port', type=int, help='Listening port for HTTP Server')
  parser.add_argument('ip', help='HTTP Server IP')
  args = parser.parse_args()
  
  print "Reading the data....."
  data = LocalData()
  
  server = SimpleHttpServer(args.ip, args.port)
  print 'HTTP Server Running...........'
  server.start()
  server.waitForThread()
  