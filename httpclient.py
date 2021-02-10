#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.splitlines()[0].split()[1]
        return int(code)

    def get_headers(self,data):
        body_index = data.find("\r\n\r\n")
        status_index = data.find("\r\n")
        headers = data[status_index:body_index]
        return headers

    def get_body(self, data):
        body_index = data.find("\r\n\r\n")
        body = data[body_index:]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        location = urllib.parse.urlparse(url)
        #print ("Location info: " + location.netloc + location.hostname + location.port)
        final_host = ''
        if location.netloc == '':
            final_host = location.path.split("/")[0]
            final_path = location.path[location.path.index("/"):]
        else:
            if location.path == '':
                final_path = '/'
            else:
                final_path = location.path
            final_host = location.hostname
        print(final_host, location.netloc)

        if location.port != None:
            self.connect(final_host, int(location.port))
        else:
            print("No port provided, default 80")
            self.connect(final_host, 80)
        
        request = "GET " + final_path + " HTTP/1.1\r\nHost: " + final_host + "\r\nAccept: */*\r\nConnection: close\r\n\r\n"
        print("Sending: \n" + request)
        self.sendall(request)
        print("Sent Request, Waiting for Response.")
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)
        # print(response)
        print("Status Code:\r\n" + str(code))
        print("Headers Received:\r\n" + headers)
        print("Body Received:\r\n" + body)
        self.close()
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        location = urllib.parse.urlparse(url)
        if location.port != None:
            self.connect(location.hostname, int(location.port))
        else:
            self.connect(location.hostname, 80)
        if location.path == '':
            final_path = '/'
        else:
            final_path = location.path
        request = "POST " + final_path + " HTTP/1.1\r\nHost: " + location.netloc + "\r\nConnection: close\r\n"
        if args != None:
            content = ''
            for item in args.items():
                content += item[0] + "=" + item[1] + "&"
            content.rstrip("&")
            print(content)
            request += "Content-Type: application/x-www-form-urlencoded\r\nContent-Length: " + str(len(content)) + "\r\n\r\n" + content
        else:
            request += "Content-Length: 0\r\n\r\n"
        print(request)
        self.sendall(request)
        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)
        # print(response)
        print("Status Code:\r\n" + str(code))
        print("Headers Received:\r\n" + headers)
        print("Body Received:\r\n" + body)
        self.close()
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
