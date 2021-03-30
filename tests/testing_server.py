import os
import subprocess
import time

FNULL = open(os.devnull, "w")
server = None


def start_server(verbose=False):
    global server
    print("VEEDRIVE_MEDIA_PATH configured as:", os.getenv("VEEDRIVE_MEDIA_PATH"))
    if verbose:
        server = subprocess.Popen(["python3", "-m", "veedrive.main"])
    else:
        server = subprocess.Popen(
            ["python3", "-m", "veedrive.main"], stdout=FNULL, stderr=FNULL
        )
    time.sleep(2)


def kill_server():
    server.terminate()
    FNULL.close()
