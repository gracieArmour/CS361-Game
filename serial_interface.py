import subprocess as sp
import struct
import json
import time

# CONSTANTS
## Points consts
PNT_REQUEST_FILE = "../Points-Microservice/points_request.json"
PNT_RESPONSE_FILE = "../Points-Microservice/points_response.json"

## Sign consts
SGN_REQUEST_FILE = ""
SGN_RESPONSE_FILE = ""

## Death Message consts
DTH_REQUEST_FILE = ""
DTH_RESPONSE_FILE = ""

## High score consts
HSC_REQUEST_FILE = ""
HSC_RESPONSE_FILE = ""


# GLOBAL VARS
waiting = {
    'pnt': {
        'waiting': False,
        'pipe_state': ''
    },
    'sgn': {
        'waiting': False,
        'pipe_state': 0
    },
    'dth': {
        'waiting': False,
        'pipe_state': 0
    },
    'hsc': {
        'waiting': False,
        'pipe_state': 0
    }
}
response_queue = []

# FUNCTION DEFINITIONS
## SEND/RECEIVE HELPER FUNCTIONS
def send_str(string):
    game.stdin.write(len(string).to_bytes(2, 'little'))
    game.stdin.flush()
    game.stdin.write(string.encode('utf-8'))
    game.stdin.flush()

def send_call(string):
    game.stdin.write(string.encode('utf-8'))
    game.stdin.flush()

def recv_str(length):
    return game.stdout.read(length).decode('utf-8')

def send_int(num):
    game.stdin.write(num.to_bytes(2, 'little'))
    game.stdin.flush()

def recv_int():
    return struct.unpack('<1h', game.stdout.read(2))[0]

## HANDLER FUNCTIONS
def handle_request():
    handshake = recv_str(3)

    match (handshake):
        case 'nil':
            return
        case 'pnt':
            pnt_request()
        case 'sgn':
            sgn_request()
        case 'dth':
            dth_request()
        case 'hsc':
            hsc_request()

def pnt_request():
    print("Calling Points Service...")

    # get request data
    points_request = {}

    points_request['points_id'] = recv_str(3)
    request_type = recv_str(1)
    if (request_type == 'g'):
        points_request['request_type'] = 'GET'
    else:
        points_request['request_type'] = 'POST'
    points_request['added_points'] = recv_int()

    print(points_request) # DEBUG

    # store current pipe state for listener
    with open(PNT_RESPONSE_FILE, "r", encoding="utf-8") as f:
        waiting['pnt']['pipe_state'] = f.read()

    # send request to Points Microservice
    with open(PNT_REQUEST_FILE, "w", encoding="utf-8") as f:
        json.dump(points_request, f)
    
    # enable response pipe listener
    waiting['pnt']['waiting'] = True

def sgn_request():
    print("Calling Sign Service...")

def dth_request():
    print("Calling Death Message Service...")

def hsc_request():
    print("Calling High Score Service...")


def handle_response():
    if (0 == len(response_queue)):
        service = 'nil'
    else:
        response = response_queue.pop(0)
        service = response['service']
    
    send_str(service)

    match (service):
        case 'nil':
            return
        case 'pnt':
            pnt_response(response)
        case 'sgn':
            sgn_response(response)
        case 'dth':
            dth_response(response)
        case 'hsc':
            hsc_response(response)

def pnt_response(response):
    send_int(response['Points'])

def sgn_response(response):
    pass

def dth_response(response):
    pass

def hsc_response(response):
    pass


def handle_queue():
    if (waiting['pnt']['waiting']):
        with open(PNT_RESPONSE_FILE, "r", encoding="utf-8") as f:
            new_state = f.read()
        
        if (new_state != waiting['pnt']['pipe_state']):
            with open(PNT_RESPONSE_FILE, "r", encoding="utf-8") as f:
                points_response = json.load(f)
            response_queue.append({
                'service': 'pnt',
                'Points': points_response['Points']
            })
            waiting['pnt']['waiting'] = False

    if (waiting['sgn']['waiting']):
        with open(SGN_RESPONSE_FILE, "r", encoding="utf-8") as f:
            new_state = json.load(f)
        
        if (new_state['req_id'] != waiting['sgn']['pipe_state']):
            pass

    if (waiting['dth']['waiting']):
        with open(DTH_RESPONSE_FILE, "r", encoding="utf-8") as f:
            new_state = json.load(f)
        
        if (new_state['req_id'] != waiting['dth']['pipe_state']):
            pass

    if (waiting['hsc']['waiting']):
        with open(HSC_RESPONSE_FILE, "r", encoding="utf-8") as f:
            new_state = json.load(f)
        
        if (new_state['req_id'] != waiting['hsc']['pipe_state']):
            pass


# start pico-8 and cartridge as subprocess
game = sp.Popen([r"C:\Program Files (x86)\PICO-8\pico8.exe",
                "-run",
                r".\cs391_adv_game.p8.png"],
               stdin=sp.PIPE, stdout=sp.PIPE)


# MAIN LOOP
while True:
    handle_request()
    handle_response()
    handle_queue()

