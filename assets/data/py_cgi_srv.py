# Python HTTP Python CGI server
# py_cgi_srv.py
# my.opera.com/devloop - 09/2010
import time
import BaseHTTPServer
import os
import cgi
import urlparse
import sys

# path to the python interpreter
#python_path = "python"
python_path = "D:\\Python\\App\\python.exe"

# path where your web files are
#wwwroot = "/tmp/www"
wwwroot = "D:\\www"

# Hostname. If empty will use any interfaces
HOST_NAME = ''
# TCP port number
PORT_NUMBER = 8888

# Handler used to manage the HTTP methods
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    # directory listing
    def generate_index(s):
        link = "<a href=\"%s\">%s</a><br />\n"
        for x in os.listdir(wwwroot + os.sep + s.path):
            if os.path.isdir(wwwroot + os.sep + s.path + os.sep + x):
                s.wfile.write(link % ((x + '/'), x))
            else:
                s.wfile.write(link % (x, x))

    # return 404 error code
    def file_not_found(s):
        s.send_response(404)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("Not found")

    # process GET requests
    def do_GET(s):
        fpath = s.path
        if s.path.find("?") != -1:
            fpath = s.path.split("?", 1)[0]

        os.environ["REQUEST_METHOD"] = "GET"
        if os.path.isdir(wwwroot + os.sep + fpath):
            if not fpath.endswith('/'):
                s.send_response(301)
                s.send_header("Location", fpath + '/')
                s.end_headers()
                return
            else:
                s.send_response(200)
                s.send_header("Content-type", "text/html")
                s.end_headers()
                s.generate_index()
        elif os.path.isfile(wwwroot + os.sep + fpath):
            s.process_request()
        else:
            s.file_not_found()
    
    # process HEAD requests
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    # do the main job
    def process_request(s):
        qs = ""
        fpath = s.path
        if s.path.find("?") != -1:
            fpath , qs = s.path.split("?", 1)

        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        # Fill the environment variables
        if s.headers.get("user-agent") != None:
            os.environ["HTTP_USER_AGENT"] = s.headers.get("user-agent")
        if s.headers.get("referer") != None:
            os.environ["HTTP_REFERER"] = s.headers.get("referer")
            
        if s.headers.get("content-type") != None:
            os.environ["CONTENT_TYPE"] = s.headers.get("content-type")
            if os.environ["CONTENT_TYPE"] == "application/x-www-form-urlencoded":
                if s.headers.get("content-length") != None:
                    os.environ["CONTENT_LENGTH"] = s.headers.get("content-length")
                    if os.environ["CONTENT_LENGTH"].isdigit():
                        qs = s.rfile.read(int(os.environ["CONTENT_LENGTH"]))
                            
        os.environ["SCRIPT_NAME"] = fpath
        os.environ["QUERY_STRING"] = qs
        
        ext = ""
        if fpath.find(".") != -1:
            ext = fpath.rsplit(".", 1)[1]
        
        sys.stderr = sys.stdout
        # If it's a python file, execute it
        if ext == "py":
            if os.path.isfile(wwwroot + os.sep + fpath):
                cmd = python_path + " " + wwwroot + os.sep + fpath
                s.wfile.write(os.popen(cmd).read())
        # else just dump the content
        else:
            if os.path.isfile(wwwroot + os.sep + fpath):
                s.wfile.write(open(wwwroot + os.sep + fpath, 'r').read())

    # process POST requests
    def do_POST(s):
        os.environ["REQUEST_METHOD"] = "POST"
        s.process_request()

# main loop
if __name__ == '__main__':
    print "Python HTTP CGI server - devloop"
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
