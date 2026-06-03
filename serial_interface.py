import subprocess as sp
import struct

# FUNCTION DEFINITIONS
def send_str(string):
    game.stdin.write(string.encode('utf-8'))
    game.stdin.flush()

def recv_str(length):
    return game.stdout.read(length).decode('utf-8')

def send_int(num):
    game.stdin.write(num)
    game.stdin.flush()

def recv_int():
    return struct.unpack('<1h', game.stdout.read(2))[0]


# start pico-8 and cartridge as subprocess
game = sp.Popen([r"C:\Program Files (x86)\PICO-8\pico8.exe",
                "-run",
                r".\cs391_adv_game.p8.png"],
               stdin=sp.PIPE, stdout=sp.PIPE)

# MAIN LOOP
while True:
    service = recv_str(3)

    match (service):
        case 'pnt': # Points Service
            print("Calling Points Service...")
            points_id = recv_str(3)
            request_type = recv_str(1)
            if request_type == 'g':
                request_type = "GET"
            else:
                request_type = "POST"
            added_points = recv_int()

            print(points_id, request_type, added_points)

            send_str('hello')
        case 'sgn': # Sign Service
            print("Calling Sign Service...")
        case 'dth': # Random Death Message Service
            print("Calling Random Death Message Service...")
        case 'hsc': # High Score Service
            print("Calling High Score Service...")
        case _:
            pass
    
    service=''
