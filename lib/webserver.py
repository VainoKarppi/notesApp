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
            headers = self.GetHeaders()

            method = headers['Method']
            path = headers["Referer"]
            baseurl = "/".join((path.split('/')[0:3])).strip()
            subDir = "/" + "".join((path.split('/')[3:])).strip().split('?')[0]
            parameters = self.ParseParameters(path)

            if (method.lower() != "get"): raise NotImplementedError(f"{method} not implemented yet!")


            headers = {
                "Content-Type": "text/plain",
                "Server": "NotesApp API",
            }
    
            print("LOGIN SUCCESS")
            http_response = build_http_response(HTTPStatus.OK, headers, json_data)
            self.request.sendall(http_response)
        except Exception as e:
            headers = {
                "Content-Type": "application/json",
                "Server": "NotesApp API",
                "WWW-Authenticate": "Basic",
            }

            if isinstance(e, NotAuthenticatedException):
                http_response = self.BuildResponse(HTTPStatus.UNAUTHORIZED, headers,str(e))
            elif isinstance(e, SiteNotFound):
                http_response = self.BuildResponse(HTTPStatus.NOT_FOUND, headers,str(e))
            elif isinstance(e, NotImplementedError):
                http_response = self.BuildResponse(HTTPStatus.NOT_IMPLEMENTED, headers,str(e))
            else:
                http_response = self.BuildResponse(HTTPStatus.INTERNAL_SERVER_ERROR, headers,str(e))


            print(e)
            self.request.sendall(http_response)
        
        print("REQUEST END")
    def GetHeaders(self):
        data = self.request.recv(1024).decode('utf-8')
        headers = {}
        headerLines = data.split('\n')

        headers["Method"] = headerLines[0].split(' ')[0].strip()

        for line in headerLines:
            if (':' not in line): continue
            key, value = line.split(': ')
            headers[key] = value
        
        if ("Referer" not in headers):
            headerRequest = headerLines[0].split(' ')
            baseAddress = f"{self.server.server_address[0]}:{self.server.server_address[1]}"
            if ("Host" in headers): baseAddress = f"{headers['Host']}"
            headers["Referer"] = (f"http://{baseAddress.strip()}{headerRequest[1].strip()}").strip()
        
        if (self.DEBUG): print(f"\nREQUEST: {self.client_address} -> {headerLines[0]}\nHEADERS:\n{headers}")

        return headers

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

class NotAuthenticatedException(Exception):
    pass

class SiteNotFound(Exception):
    pass