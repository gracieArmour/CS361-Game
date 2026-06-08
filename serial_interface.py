import subprocess as sp
import struct
import json
import time
import random
from datetime import datetime
import math

# CONSTANTS
## Points consts
PNT_REQUEST_FILE = "../Points-Microservice/points_request.json"
PNT_RESPONSE_FILE = "../Points-Microservice/points_response.json"

## Sign consts
SGN_REQUEST_FILE = "../Signs-Microservice/signs_request.json"
SGN_RESPONSE_FILE = "../Signs-Microservice/signs_response.json"

## Death Message consts
DTH_REQUEST_FILE = "../Death-Message-Microservice/death_message_request.json"
DTH_RESPONSE_FILE = "../Death-Message-Microservice/death_message_response.json"

## High score consts
HSC_REQUEST_FILE = "../High-Score-Microservice/high_score_request.json"
HSC_RESPONSE_FILE = "../High-Score-Microservice/high_score_response.json"


# GLOBAL VARS
waiting = {
    'pnt': {
        'waiting': False,
        'pipe_state': ''
    },
    'sgn': {
        'waiting': False,
        'req_id': 0
    },
    'dth': {
        'waiting': False,
        'req_id': 0
    },
    'hsc': {
        'waiting': False,
        'req_id': 0
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
        points_request['request_type'] = 'get'
    else:
        points_request['request_type'] = 'post'
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
    request_id = math.floor(random.random() * 9998) + 1

    signs_request = {}
    signs_request['req_id'] = request_id
    signs_request['x'] = recv_int()
    signs_request['y'] = recv_int()

    # send request to Signs Microservice
    with open(SGN_REQUEST_FILE, "w", encoding="utf-8") as f:
        json.dump(signs_request, f)
    
    # enable response pipe listener
    waiting['sgn']['req_id'] = request_id
    waiting['sgn']['waiting'] = True

def dth_request():
    print("Calling Death Message Service...")
    request_id = math.floor(random.random() * 9998) + 1
    
    death_message_request = {}
    death_message_request['req_id'] = request_id

    # send request to Death Message Microservice
    with open(DTH_REQUEST_FILE, "w", encoding="utf-8") as f:
        json.dump(death_message_request, f)
    
    # enable response pipe listener
    waiting['dth']['req_id'] = request_id
    waiting['dth']['waiting'] = True

def hsc_request():
    print("Calling High Score Service...")
    request_id = math.floor(random.random() * 9998) + 1

    high_score_request = {}

    high_score_request['req_id'] = request_id
    request_type = recv_str(1)
    if (request_type == "g"):
        high_score_request['type'] = 'get'
    else:
        high_score_request['type'] = 'post'
        high_score_request['name'] = recv_str(3)
        high_score_request['points'] = recv_int()
    
    # send request to Death Message Microservice
    with open(HSC_REQUEST_FILE, "w", encoding="utf-8") as f:
        json.dump(high_score_request, f)
    
    # enable response pipe listener
    waiting['hsc']['req_id'] = request_id
    waiting['hsc']['waiting'] = True


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
    num_lines = len(response['lines'])
    send_int(num_lines)
    for i in range(0,num_lines):
        send_str(response['lines'][i])
    

def dth_response(response):
    send_str(response['message'])

def hsc_response(response):
    send_str(response['type'])
    
    if ('get'==response['type']):
        send_str(response['highscore'])
    else:
        num_entries = len(response['entries'])
        send_int(num_entries)
        for entry in response['entries']:
            send_str(entry['name'])
            send_int(entry['points'])


def handle_queue():
    global waiting
    global response_queue

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
        empty_response = False
        with open(SGN_RESPONSE_FILE, "r", encoding="utf-8") as f:
            contents = f.read()
            if (contents != ""):
                new_state = json.loads(contents)
            else:
                empty_response = True
        
        if ((not empty_response) and (new_state['req_id'] == waiting['sgn']['req_id'])):
            response_queue.append({
                'service': 'sgn',
                'lines': new_state['lines']
            })
            waiting['sgn']['waiting'] = False

    if (waiting['dth']['waiting']):
        empty_response = False
        with open(DTH_RESPONSE_FILE, "r", encoding="utf-8") as f:
            contents = f.read()
            if (contents != ""):
                new_state = json.loads(contents)
            else:
                empty_response = True
        
        if ((not empty_response) and (new_state['req_id'] == waiting['dth']['req_id'])):
            response_queue.append({
                'service': 'dth',
                'message': new_state['message']
            })
            waiting['dth']['waiting'] = False

    if (waiting['hsc']['waiting']):
        empty_response = False
        with open(HSC_RESPONSE_FILE, "r", encoding="utf-8") as f:
            contents = f.read()
            if (contents != ""):
                new_state = json.loads(contents)
            else:
                empty_response = True
        
        if ((not empty_response) and (new_state['req_id'] == waiting['hsc']['req_id'])):
            pass


# INIT LOOP
pipes_started = [False,False, False,False, False,False, False,False]
all_pipes = [PNT_REQUEST_FILE,PNT_RESPONSE_FILE, SGN_REQUEST_FILE,SGN_RESPONSE_FILE, DTH_REQUEST_FILE,DTH_RESPONSE_FILE, HSC_REQUEST_FILE,HSC_RESPONSE_FILE]
# while not all(pipes_started):
#     for i, pipe in enumerate(all_pipes):
#         try:
#             with open(pipe, "r", encoding="utf-8") as f:
#                 content = f.read()
#         except Exception:
#             continue
#         pipes_started[i] = True
            

# start pico-8 and cartridge as subprocess
game = sp.Popen([r"C:\Program Files (x86)\PICO-8\pico8.exe",
                "-run",
                r".\cs391_adv_game.p8.png"],
               stdin=sp.PIPE, stdout=sp.PIPE)

# seed randomizer for request ids
random.seed(datetime.now().timestamp())

# MAIN LOOP
while True:
    handle_request()
    handle_response()
    handle_queue()

