import os
import subprocess
from importlib.util import find_spec
from importlib.metadata import version

def get_version():
    try:
        return subprocess.run(
            'git describe --tags', 
            shell=True, 
            check=True, 
            capture_output=True,
            cwd=os.path.dirname(find_spec('flightanalysis').origin) 
        ).stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return version('flightanalysis')
    
__version__ = get_version() 