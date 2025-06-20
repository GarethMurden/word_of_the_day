import os
import socket
import qrcode

dirname, scriptname = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        address = s.getsockname()[0]
    except Exception:
        address = '127.0.0.1'
    finally:
        s.close()
    return address

def get_address():
    url = f'http://{get_ip()}:5000'
    qr_code = qrcode.make(url)
    save_as = f'{THIS_DIRECTORY}qr.png'
    qr_code.save(save_as)
    return url, save_as
