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
        code = data.splitlines()[0].split()[1] # Split lines in response, first line will contain status code after HTTP/1.1, so split spaces and retrieve second element
        return int(code) # Return integer form of status code

    def get_headers(self,data):
        body_index = data.find("\r\n\r\n") # Find start of body
        status_index = data.find("\r\n") # Find first newline after the status line of HTTP response
        headers = data[status_index:body_index] # Splice response from after status line ot start of body
        return headers

    def get_body(self, data):
        body_index = data.find("\r\n\r\n") # Find start of body
        body = data[body_index:] # Splice response form start of body onwards
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
        try: # Catch any exception while parsing the user's url
            location = urllib.parse.urlparse(url) # Use urllib to parse the query entered in the argument
            final_host = ''
            if location.netloc == '':
                # If there is no netloc, then path will contain host, use string parsing to find correct host
                final_host = location.path.split("/")[0]
                final_path = location.path[location.path.index("/"):]
            else:
                # If there is no path after the host, just send a /, otherwise retrieve path
                if location.path == '':
                    final_path = '/'
                else:
                    final_path = location.path
                final_host = location.hostname

            # Check if urllib was able to find a port provided in the url, if not then use port 80 for http
            if location.port != None:
                self.connect(final_host, int(location.port))
            else:
                self.connect(final_host, 80)

            # Formulate request based on parameters extracted from url above
            request = "GET " + final_path + " HTTP/1.1\r\nHost: " + final_host + "\r\nAccept: */*\r\nAccept-Charset: utf-8\r\nConnection: close\r\n\r\n"
        except Exception as e: # If an exception occurred, return code 500
            print("Encountered: " + str(e) + ", while parsing url.")
            code = 500
            body = ''
        else:
            # Send the request to the specified url
            self.sendall(request)
            # Read in the data sent back from the http server
            response = self.recvall(self.socket)

            # Get the status code from the response
            code = self.get_code(response)
            # Get the body from the response
            body = self.get_body(response)
            # Get the headers from the response
            headers = self.get_headers(response)

            # Print out data that was returned from the server
            print("Status Code:\r\n" + str(code))
            print("Headers Received:\r\n" + headers)
            print("Body Received:\r\n" + body)
            self.close() # Close the connection with the server
        
        return HTTPResponse(code, body) # Return HTTPResponse object with the body and code of the response

    def POST(self, url, args=None):
        code = 500
        body = ""
        try: # Catch any exception while parsing the user's url
            location = urllib.parse.urlparse(url) # Use urllib to parse the query entered in the argument
            
            final_host = ''
            if location.netloc == '':
                # If there is no netloc, then path will contain host, use string parsing to find correct host
                final_host = location.path.split("/")[0]
                final_path = location.path[location.path.index("/"):]
            else:
                # If there is no path after the host, just send a /, otherwise retrieve path
                if location.path == '':
                    final_path = '/'
                else:
                    final_path = location.path
                final_host = location.hostname
            
            # Check that the port contains a value, if not use default port 80 for http
            if location.port != None:
                self.connect(final_host, int(location.port))
            else:
                self.connect(final_host, 80)
            
            # Build beginning of request headers
            request = "POST " + final_path + " HTTP/1.1\r\nHost: " + location.netloc + "\r\nConnection: close\r\n"
            
            # If arguments were included in the POST, translate them into a query string format and append relevant information to the headers
            if args != None:
                content = urllib.parse.urlencode(args)
                # Add the necessary headers for the url encoded body
                request += "Content-Type: application/x-www-form-urlencoded\r\nContent-Length: " + str(len(content)) + "\r\n\r\n" + content
            else:
                # If there is no body, use content length to convey to server that body for POST is empty
                request += "Content-Length: 0\r\n\r\n"
        except Exception as e: # Catch any exceptions during url parsing and request building
            print("Encountered: " + str(e) + ", while parsing url.")
            code = 500
            body = ''
        else:
            self.sendall(request) # send request to server

            response = self.recvall(self.socket) # Read in response form the server

            code = self.get_code(response) # Parse the status code from the http server's response
            body = self.get_body(response) # Parse the body of the response
            headers = self.get_headers(response) # Parse the headers of the response

            # Print out information from the repsonse
            print("Status Code:\r\n" + str(code))
            print("Headers Received:\r\n" + headers)
            print("Body Received:\r\n" + body)
            self.close() # Close connection to the http server
        
        return HTTPResponse(code, body) # Return HTTPResponse with code and body from response

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
