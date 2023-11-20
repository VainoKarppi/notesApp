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
import lib.notes as notes


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID): return obj.hex
        if isinstance(obj, datetime): return str(obj)
        return json.JSONEncoder.default(self, obj)



class MyRequestHandler(socketserver.BaseRequestHandler):
    DEBUG = False
    PAGES = ["/","/notes","/note"]

    def HandleClientRequest(self,user:accounts.Account, method:str, baseurl:str, subDir:str, parameters: dict[str,str]):
        # TODO Spawn in a new thread
        method = method.lower()
        subDir = subDir.lower()
        if(subDir == "/notes" or subDir == "/"):
            allnotes = notes.GetAllUserNotes(user.uuid)
            json_string = json.dumps([ob.__dict__ for ob in allnotes],cls=UUIDEncoder)
            return json_string
        
        if(subDir == "/note"):
            subject = parameters["subject"]
            note = notes.GetNote(user.uuid,subject)
            if (note is None): raise SiteNotFound("This note was not found!")
            return json.dumps(note.__dict__,cls=UUIDEncoder)
        

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

            json_data = self.HandleClientRequest(user,method,baseurl,subDir,parameters)
            

            headers = {
                "Content-Type": "application/json",
                "Server": "NotesApp API",
                "WWW-Authenticate": "Basic",
            }
    
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

            self.request.sendall(http_response)

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
        while True:
            data = self.request.recv(1024)
            if (not data): break

            data = data.strip().decode('utf-8')
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

    def ParseParameters(self, requestUrl:str) -> dict[str,str]:
        parameters = {}
        for param in "".join((requestUrl.split('?')[1:])).split('&'):
            if ('=' not in param): continue
            key, value = param.split('=')
            parameters[key.lower().strip()] = value.strip()

        return parameters


def RunServer(ip,port):
    global Server
    with socketserver.ThreadingTCPServer((ip, port), MyRequestHandler) as Server:
        Server.serve_forever()

def StartServer(ip,port):
    thread = threading.Thread(target=RunServer, args=(ip,port,))
    thread.start()
    print (f"WEB Server started at {ip}:{port}")

def StopServer():
    Server.server_close()
    Server.shutdown()


class NotAuthenticatedException(Exception):
    pass

class SiteNotFound(Exception):
    pass