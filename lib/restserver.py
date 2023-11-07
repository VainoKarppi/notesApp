import json
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
import threading

class Handler (http.server.SimpleHTTPRequestHandler):

    def __init__ (self, request: bytes, client_address: Tuple [str, int], server: socketserver.BaseServer):
        super().__init__ (request, client_address, server)

    @property
    def api_response (self):
        return json.dumps ({"message": "Hello world"}).encode()

    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes (self.api_response))
    


def RunServer(port):
    global Server
    Server = socketserver.TCPServer (("0.0.0.0", port), Handler)
    Server.serve_forever()

def StartServer(port):
    thread = threading.Thread(target=RunServer, args=(port,))
    thread.start()
    print (f"REST Server started at port {port}")

def StopServer():
    Server.shutdown()
    Server.server_close()