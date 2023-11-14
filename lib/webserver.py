import base64
import json
import uuid
import http.server
import os
import secrets
import socketserver
import string
from typing import Any, Tuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from datetime import datetime
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
    DEBUG = True
    PAGES = ["/","/notes","/note"]

    def handle(self):
        try:
            headers = self.GetHeaders()

            method = headers['Method']
            path = headers["Referer"]
            baseurl = "/".join((path.split('/')[0:3])).strip()
            subDir = "/" + "".join((path.split('/')[3:])).strip().split('?')[0]
            parameters = self.ParseParameters(path)

            if (method.lower() != "get"): raise NotImplementedError(f"{method} not implemented yet!")


            user = self.Authenticate(headers)
            if (subDir.lower() not in self.PAGES): raise SiteNotFound(f"{subDir} is not a valid sub directory path")


            headers = {
                "Content-Type": "application/json",
                "Server": "NotesApp API",
                "WWW-Authenticate": "Basic",
            }
    
            print(f"LOGIN SUCCESS: {user.name}")
            http_response = self.BuildResponse(HTTPStatus.OK, headers, json_data)
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

    def Authenticate(self, headers) -> accounts.Account:
        try:
            if ("Authorization" not in headers): raise NotAuthenticatedException("No Access")
            auth_data = headers["Authorization"][6:] # "Basic bXl1c2VybmFtZTpteXBhc3N3b3Jk" --> "bXl1c2VybmFtZTpteXBhc3N3b3Jk"
            username, password = base64.b64decode(auth_data).decode('utf-8').split(':')
            user = accounts.Login(username,password)
            return user
        except:
            raise NotAuthenticatedException(headers)


    def BuildResponse(self, status: HTTPStatus, headers:dict[str,str] = None, body:str = None) -> bytes:
        response = f"HTTP/1.1 {status._value_} {status.phrase}\r\n"

        if (headers is not None):
            for header, value in headers.items(): response += f"{header}: {value}\r\n"

        if (body is None): body = status.phrase
        response += "\r\n" + body

        if (self.DEBUG): print(f"\nRESPONSE: ({self.client_address}) --> STATUS:{status._value_} -> HEADERS:{headers} -> BODY:{body}")

        return response.encode('utf-8')
    

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
    Server = socketserver.TCPServer(("127.0.0.1", port), MyRequestHandler)
    Server.serve_forever()

def StartServer(port):
    thread = threading.Thread(target=RunServer, args=(port,))
    thread.start()
    print (f"WEB Server started at port {port}")

def StopServer():
    Server.server_close()
    Server.shutdown()


class NotAuthenticatedException(Exception):
    pass

class SiteNotFound(Exception):
    pass