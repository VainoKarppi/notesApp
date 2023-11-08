import base64
import json
import http.server
import os
import socketserver
from typing import Any, Tuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import threading
import lib.sqlitedb as db
import lib.accounts as accounts

class Handler (http.server.BaseHTTPRequestHandler):
    def __init__ (self, request: bytes, client_address: Tuple [str, int], server: socketserver.BaseServer):
        super().__init__ (request, client_address, server)

    # Stop logs
    def log_message(self, format: str, *args: Any) -> None:
        #return super().log_message(format, *args)
        return None
    
    @property
    def api_response (self):
        return json.dumps({"message": "Hello world"}).encode()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = User.ParseInputData(self.rfile.read(content_length))
            if (self.path == "/login"):
                account = User.Authenticate(data["username"],data["password"])
                if(account is None):
                    self.send_response(HTTPStatus.UNAUTHORIZED)
                    self.end_headers()

                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', 'application/json')
                self.send_header('Set-Cookie', "authorized=1") # TODO send something to check if the server has restarted
                self.end_headers()
                self.wfile.write(bytes(self.api_response))
                
        except Exception as e:
            print(e)
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.end_headers()
        
    def do_GET(self):
        print("GET REQUEST")
        if (self.path not in WebView.Paths):
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return
        
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        if (self.path == "/"): self.wfile.write(bytes(WebView.LoginPage(),"utf-8"))
        if (self.path == "/test"): self.wfile.write(bytes(WebView.TestPage(),"utf-8"))

class User:
    def ParseInputData(data):
        splitted = data.decode('utf-8').split('&')

        data = {}
        for pair in splitted:
            key, value = pair.split('=')
            data[key] = value

        return data

    def Authenticate(username:str, password:str) -> accounts.Account:
        account = accounts.Login(username,password)
        return account

class WebView:
    global Dir_path
    Paths = ["/","/test"]
    Dir_path = os.path.dirname(os.path.realpath(__file__))
    def LoginPage():
        html_path = os.path.join(Dir_path, "../html/login.html")
        with open(html_path, "r") as f:
            return f.read()

    
    def TestPage():
        return "<body><p>This is a test.</p>"


def RunServer(port):
    global Server
    Server = socketserver.TCPServer(("0.0.0.0", port), Handler)
    Server.serve_forever()

def StartServer(port):
    thread = threading.Thread(target=RunServer, args=(port,))
    thread.start()
    print (f"WEB Server started at port {port}")

def StopServer():
    Server.shutdown()
    Server.close_request()