import base64
import json
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import threading
import lib.sqlitedb as db
import lib.accounts as accounts

class Handler (http.server.BaseHTTPRequestHandler):

    def __init__ (self, request: bytes, client_address: Tuple [str, int], server: socketserver.BaseServer):
        super().__init__ (request, client_address, server)

    @property
    def api_response (self):
        return json.dumps({"message": "Hello world"}).encode()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))

            type = data["type"]
            if (type.lower() == "login"):
                account = User.Authenticate(data["username"],data["password"])
                if(account is None):
                    self.send_response(HTTPStatus.UNAUTHORIZED)
                    self.end_headers()

                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(self.api_response))
                
        except:
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.end_headers()
    
class User:
    def Authenticate(username:str, password:str) -> accounts.Account:
        account = accounts.Login(username,password)
        return account


def RunServer(port):
    global Server
    Server = socketserver.TCPServer(("0.0.0.0", port), Handler)
    Server.socket_type
    Server.serve_forever()

def StartServer(port):
    thread = threading.Thread(target=RunServer, args=(port,))
    thread.start()
    print (f"REST Server started at port {port}")

def StopServer():
    Server.shutdown()
    Server.server_close()