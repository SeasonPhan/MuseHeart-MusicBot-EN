# -*- coding: utf-8 -*-
from platform import python_version

from utils.client import BotPool

print(f"🐍 - Python version: {python_version()}")

pool = BotPool()

pool.setup()
