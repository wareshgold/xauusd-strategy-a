"""Audit-only pytest plugin: no real network/MT5, no credentials supplied."""
import os
import sys
import importlib.util

for key in list(os.environ):
    if any(word in key.upper() for word in ('TOKEN', 'SECRET', 'PASSWORD', 'TELEGRAM', 'ACCOUNT', 'MT5_LOGIN')):
        os.environ.pop(key, None)
os.environ['LIVE_TRADING_ENABLE'] = 'false'
os.environ['ALLOW_REAL_EXECUTION'] = 'false'
if importlib.util.find_spec('MetaTrader5') is not None:
    raise RuntimeError('Audit environment must not contain the real MetaTrader5 package')

def deny_network(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise RuntimeError('Offline audit blocked network access')
sys.addaudithook(deny_network)
