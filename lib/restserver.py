import base64
import json
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import threading

class Handler (http.server.BaseHTTPRequestHandler):

    def __init__ (self, request: bytes, client_address: Tuple [str, int], server: socketserver.BaseServer):
        super().__init__ (request, client_address, server)

    @property
    def api_response (self):
        return json.dumps({"message": "Hello world"}).encode()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(content_length))

        print(data)
        print(data["username"])
        print(data["password"])

        if self.headers.get("Authorization") == "token":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(self.api_response))
            
        else:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Bearer realm="example"')
            self.end_headers()
    


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