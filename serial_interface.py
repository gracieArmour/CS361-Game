import subprocess as sp

game = sp.Popen([r"C:\Program Files (x86)\PICO-8\pico8.exe",
                "-run",
                r".\cs391_adv_game.p8.png"],
               stdin=sp.PIPE, stdout=sp.PIPE)

while True:
    service = game.stdout.read(3)

    match (service):
        case b'pnt': # Points Service
            print("Calling Points Service...")
        case b'sgn': # Sign Service
            print("Calling Sign Service...")
        case b'dth': # Random Death Message Service
            print("Calling Random Death Message Service...")
        case b'hsc': # High Score Service
            print("Calling High Score Service...")
        case _:
            pass
