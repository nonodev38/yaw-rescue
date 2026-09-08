"""Background server runner used by the Tkinter panel (étape P2.6).

The panel starts the HTTPS server inside a daemon thread and polls the
module-level state below to display its status (online / error / URL).
"""
import ssl
import sys
import threading

from deck.paths import SCRIPT_DIR

server_instance = None
server_thread = None
server_started = False
server_error = None


def run_server(port, no_cert, cert_port):
    """Run the HTTPS server in a background thread."""
    global server_instance, server_started, server_error
    try:
        # Import and run server components
        sys.path.insert(0, str(SCRIPT_DIR))
        import server as srv

        srv.DATA_DIR.mkdir(parents=True, exist_ok=True)
        srv.STATIC_DIR.mkdir(parents=True, exist_ok=True)

        ip = srv.get_local_ip()

        if no_cert:
            srv_instance = srv.DeckHTTPServer(("0.0.0.0", port), srv.DeckHTTPHandler)
            scheme = "http"
        else:
            cert_file, key_file = srv.generate_self_signed_cert(str(srv.CERT_DIR))
            if not cert_file or not key_file:
                server_error = "No certificate available. Use --no-cert."
                return

            srv_instance = srv.DeckHTTPServer(("0.0.0.0", port), srv.DeckHTTPHandler)
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(cert_file, key_file)
            srv_instance.socket = ctx.wrap_socket(srv_instance.socket, server_side=True)
            scheme = "https"

            srv.start_cert_download_server(cert_file, cert_port)

        # Start state watcher
        threading.Thread(target=srv.state_watcher, daemon=True).start()

        server_instance = srv_instance
        server_started = True
        srv_instance.serve_forever()

    except Exception as e:
        server_error = str(e)
        server_started = False
