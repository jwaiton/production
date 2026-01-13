from typing import Any, Dict, Iterable, Iterator, List, Tuple, Literal

import subprocess
import time
import os

from dataclasses import dataclass

@dataclass
class RunResult:
    ok       : bool
    attempts : int
    stdout   : str | None = None
    stderr   : str | None = None
    error    : str | None = None

