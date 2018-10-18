import sys
import threading
import socket
import webbrowser
import subprocess

import floyd
from floyd.log import logger as floyd_logger

if sys.version_info[0] < 3:
    import urlparse
    from BaseHTTPServer import (
        BaseHTTPRequestHandler,
        HTTPServer,
    )
    from Queue import Queue, Empty as QueueEmpty
else:
    from urllib import parse as urlparse
    from http.server import (
        BaseHTTPRequestHandler,
        HTTPServer,
    )
    from queue import Queue, Empty as QueueEmpty


class LoginServer(HTTPServer, object):
    def __init__(self, server_address, RequestHandlerClass, key_queue):
        super(LoginServer, self).__init__(server_address, RequestHandlerClass)
        self.key_queue = key_queue


class LoginHttpRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

    def do_GET(self):
        params = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        key = params.get('apikey')
        if not key:
            self.send_response(400)
            return

        self.server.key_queue.put(key[0])

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        page_content = ("""
            <html>
            <header>
             <script>
               window.location.replace("%s/cli_login?keystate=sent");
             </script>
            </header>
            </html>
        """ % (floyd.floyd_web_host)).encode('utf-8')
        self.wfile.write(page_content)

    def log_message(self, fmt, *args):
        return


def get_free_port():
    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', 0))
        (hostname, port) = s.getsockname()
        s.close()
        return (hostname, port)
    except socket.error:
        return (None, None)


def wait_for_apikey():
    floyd_logger.info('Waiting for login from browser...')

    key_queue = Queue()
    (hostname, port) = get_free_port()
    if not port:
        floyd_logger.error("Failed to allocate TCP port for automatic login.")
        return
    server = LoginServer((hostname, port), LoginHttpRequestHandler, key_queue)

    t = threading.Thread(
        target=server.serve_forever)
    t.daemon = True
    t.start()

    cli_host = 'http://' + hostname
    url = '%s/cli_login?fallback=redirect&callback=%s:%s' % (floyd.floyd_web_host, cli_host, port)
    subprocess.check_output(
        [sys.executable, '-m', 'webbrowser', url], stderr=subprocess.STDOUT)

    wait_timeout_sec = 0.5
    wait_cnt = 0
    while True:
        if wait_cnt > 60:
            floyd_logger.error("Failed to get login info from browser, please login manually by creating login key at %s/settings/apikey.", floyd.floyd_web_host)
            server.shutdown()
            sys.exit(1)
        try:
            apikey = key_queue.get(timeout=wait_timeout_sec)
            break
        except QueueEmpty:
            wait_cnt += 1

    server.shutdown()
    return apikey


def has_browser():
    try:
        webbrowser.get()
        return True
    except webbrowser.Error:
        return False
