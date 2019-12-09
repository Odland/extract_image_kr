import os
import sys

from pathlib import Path

print(Path(os.path.abspath('__file__')).parents)

