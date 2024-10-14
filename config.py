import os
from dotenv import load_dotenv

load_dotenv()

# Environment variables for camera credentials
CENTRAL_USER = os.environ.get('CENTRAL_USER')
CENTRAL_PASS = os.environ.get('CENTRAL_PASS')
WEST2_USER = os.environ.get('WEST2_USER')
WEST2_PASS = os.environ.get('WEST2_PASS')
EAST2_USER = os.environ.get('EAST2_USER')
EAST2_PASS = os.environ.get('EAST2_PASS')
OPF1_USER = os.environ.get('OPF1_USER')
OPF1_PASS = os.environ.get('OPF1_PASS')
OPF2_USER = os.environ.get('OPF2_USER')
OPF2_PASS = os.environ.get('OPF2_PASS')

Cameras = {
    'Central': {
        'user': CENTRAL_USER,
        'password': CENTRAL_PASS,
        'ip': '10.20.64.158',
        'ptz_port': 80,
        'rtsp_port': 554,
    },
    'West 2': {
        'user': WEST2_USER,
        'password': WEST2_PASS,
        'ip': '10.20.64.159',
        'ptz_port': 80,
        'rtsp_port': 554,
    },
    'East 2': {
        'user': EAST2_USER,
        'password': EAST2_PASS,
        'ip': '10.20.64.159',
        'ptz_port': 80,
        'rtsp_port': 554,
    },
    'OPF 1': {
        'user': OPF1_USER,
        'password': OPF1_PASS,
        'ip': '10.30.32.241',
        'ptz_port': 80,
        'rtsp_port': 554,
    },
    'OPF 2': {
        'user': OPF2_USER,
        'password': OPF2_PASS,
        'ip': '10.29.32.68',
        'ptz_port': 80,
        'rtsp_port': 555,
    }
}
