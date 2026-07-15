import os
import signal
import subprocess as sp

# run signs
signs_service = sp.Popen([r"python",
                r".\signs_service.py"])

# run death message
death_message_service = sp.Popen([r"python",
                r".\death_message_service.py"])

# run points
points_service = sp.Popen([r"python",
                r".\points_service.py"])

# run high score
high_score_service = sp.Popen([r"python",
                r".\high_score_service.py"])

# run serial interface (which runs game)
serial_interface = sp.Popen([r"python",
                r".\serial_interface.py"])

# the below code is pulled from a stackoverflow thread: https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    self.kill_now = True

if __name__ == '__main__':
    killer = GracefulKiller()
    while not killer.kill_now and (serial_interface.poll() == None):
        pass
    
    serial_interface.kill()
    high_score_service.kill()
    points_service.kill()
    death_message_service.kill()
    signs_service.kill()