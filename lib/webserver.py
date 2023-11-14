import base64
import json
import http.server
import os
import secrets
import socketserver
import string
from typing import Any, Tuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import threading
import lib.sqlitedb as db
import lib.accounts as accounts

def build_http_response(status: HTTPStatus, headers:dict[str,str] = None, body:str = "") -> bytes:
    # Start building the response string
    response = f"HTTP/1.1 {status._value_} {status.phrase}\r\n"

    if (headers is not None):
        for header, value in headers.items():
            response += f"{header}: {value}\r\n"

    response += "\r\n" + body
    return response.encode('utf-8')


class MyRequestHandler(socketserver.BaseRequestHandler):
    HEADERS:dict[str,str] = {}
    type = "GET"
    path = "/"
    version = None
    
    def GetHeaders(self,data:str):
        self.HEADERS = {}

        header_data_lines = data.split('\n')
        datat = header_data_lines[0].split(' ')
        self.type = datat[0]
        self.path = datat[1]
        self.version = datat[2]
        for asd in datat:
            print(asd)
        for line in header_data_lines:
            if (':' not in line): continue
            key, value = line.split(': ')
            self.HEADERS[key] = value

    def handle(self):
        try:
            data = self.request.recv(1024).decode('utf-8')
            
            print(f"\nREQUEST: {self.client_address} -> {data}")
            print(self.HEADERS)
            self.GetHeaders(data)
            print(self.HEADERS)

            print(self.path)
            
            auth_data = self.HEADERS["Authorization"][6:] # "Basic bXl1c2VybmFtZTpteXBhc3N3b3Jk" --> "bXl1c2VybmFtZTpteXBhc3N3b3Jk"
            username, password = base64.b64decode(auth_data).decode('utf-8').split(':')
            user = None

            try:
                user = accounts.Login(username,password)
            except:
                pass

            if not user:
                self.request.sendall(b'HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="Restricted"\r\n\r\n')
                return

            data = {
                'name': 'John',
                'age': 30,
                'city': 'New York'
            }

            # Convert the dictionary to a JSON object
            json_data = json.dumps(data)


            headers = {
                "Content-Type": "text/plain",
                "Server": "NotesApp API",
            }
    
            print("LOGIN SUCCESS")
            http_response = build_http_response(HTTPStatus.OK, headers, json_data)
            self.request.sendall(http_response)
        except Exception as e:
            print(e)
            http_response = build_http_response(HTTPStatus.INTERNAL_SERVER_ERROR, None, str(e))
            self.request.sendall(http_response)
            
        print("REQUEST END")
        print("REQUEST END 2")

def RunServer(port):
    global Server
    Server = socketserver.TCPServer(("0.0.0.0", port), MyRequestHandler)
    Server.serve_forever()

def StartServer(port):
    thread = threading.Thread(target=RunServer, args=(port,))
    thread.start()
    print (f"WEB Server started at port {port}")

def StopServer():
    Server.shutdown()
    Server.close_request()