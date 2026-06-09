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
        'request_id': 0
    },
    'ptr': {
        'waiting': False,
        'wait_counter': 0,
        'points_id': '',
        'request_id': 0
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
    game.stdin.write(struct.pack('<1h', num))
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
        case 'ptr':
            pnt_reset_request()
        case 'sgn':
            sgn_request()
        case 'dth':
            dth_request()
        case 'hsc':
            hsc_request()

def pnt_request():
    print("Calling Points Service...")
    request_id = math.floor(random.random() * 9998) + 1

    # get request data
    points_request = {}
    points_request['request_id'] = request_id

    points_request['points_id'] = recv_str(3)
    request_type = recv_str(1)
    if (request_type == 'g'):
        points_request['request_type'] = 'GET'
    else:
        points_request['request_type'] = 'POST'
    points_request['added_points'] = recv_int()

    # send request to Points Microservice
    with open(PNT_REQUEST_FILE, "w", encoding="utf-8") as f:
        json.dump(points_request, f)
    
    print("Points request sent: ",points_request)
    
    # enable response pipe listener
    waiting['pnt']['request_id'] = request_id
    waiting['pnt']['waiting'] = True

def pnt_reset_request():
    print("Resetting points...")
    request_id = math.floor(random.random() * 9998) + 1

    reset_request = {}
    reset_request['request_id'] = request_id
    points_id = recv_str(3)
    reset_request['points_id'] = points_id
    reset_request['request_type'] = 'GET'
    reset_request['added_points'] = 0

    # send request to Points Microservice
    with open(PNT_REQUEST_FILE, "w", encoding="utf-8") as f:
        json.dump(reset_request, f)
    
    # enable response pipe listener
    waiting['ptr']['request_id'] = request_id
    waiting['ptr']['points_id'] = points_id
    waiting['ptr']['waiting'] = True

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
        case 'ptr':
            return # no additional logic, call code is sufficent signal
        case 'sgn':
            sgn_response(response)
        case 'dth':
            dth_response(response)
        case 'hsc':
            hsc_response(response)

def pnt_response(response):
    send_int(response['Points'])
    print("Points response received: ",response)

def sgn_response(response):
    num_lines = len(response['lines'])
    send_int(num_lines)
    for i in range(0,num_lines):
        send_str(response['lines'][i])
    
def dth_response(response):
    send_str(response['message'])

def hsc_response(response):
    send_str(response['type'])
    
    if ('post'==response['type']):
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
        empty_response = False
        with open(PNT_RESPONSE_FILE, "r", encoding="utf-8") as f:
            contents = f.read()
            if (contents != ""):
                new_state = json.loads(contents)
            else:
                empty_response = True
        
        if ((not empty_response) and (new_state['request_id'] == waiting['pnt']['request_id'])):
            response_queue.append({
                'service': 'pnt',
                'Points': new_state['Points']
            })
            waiting['pnt']['waiting'] = False
    
    if (waiting['ptr']['waiting']):
        empty_response = False
        with open(PNT_RESPONSE_FILE, "r", encoding="utf-8") as f:
            contents = f.read()
            if (contents != ""):
                new_state = json.loads(contents)
            else:
                empty_response = True
        
        if ((not empty_response) and (new_state['request_id'] == waiting['ptr']['request_id'])):
            match (waiting['ptr']['wait_counter']):
                case 0:
                    reset_request = {
                        'request_id': (new_state['request_id'] + 1),
                        'points_id': waiting['ptr']['points_id'],
                        'request_type': 'POST',
                        'added_points': (new_state['Points'] * -1)
                    }

                    # send request to Points Microservice
                    with open(PNT_REQUEST_FILE, "w", encoding="utf-8") as f:
                        json.dump(reset_request, f)
                    
                    waiting['ptr']['request_id'] = new_state['request_id'] + 1
                    waiting['ptr']['wait_counter'] += 1
                
                case 1:
                    response_queue.append({
                        'service': 'ptr'
                    })

                    waiting['ptr']['wait_counter'] = 0
                    waiting['ptr']['points_id'] = ''
                    waiting['ptr']['waiting'] = False

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
            new_state['service'] = 'hsc'
            response_queue.append(new_state)
            waiting['hsc']['waiting'] = False


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
#         else:
#             pipes_started[i] = True
            

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

