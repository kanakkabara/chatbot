import asyncio
from typing import Dict, Mapping
from . transport import websocket as sock

class ServerException(Exception):
    def __init__(self, error_result, recover_message):
        self.error_message = error_result['error']['error']
        self.error_result = error_result
        self.recover_message = recover_message

class AsyncHolder:
    """
    Wrapper for sending subscriptions and methods.
    Takes callbacks or (asyncio-)block until the
    result is received.
    """
    def __init__(self):
        self.awaited_subs: Dict[str, asyncio.Future] = {}
        self.awaited_methods: Dict[str, asyncio.Future] = {}
        self.awaited_method_messages: Dict[str, Mapping] = {}

    async def send_sub(self, ws, uid: str, msg: Mapping):
        fut: asyncio.Future = asyncio.Future()
        self.awaited_subs[uid] = fut
        await sock.send(ws, msg)
        return await fut

    def send_sub_noblock(self, ws, uid: str, msg: Mapping, callback=None):
        if callback:
            fut: asyncio.Future = asyncio.Future()
            fut.add_done_callback(callback)
            self.awaited_subs[uid] = fut
        sock.send(ws, msg)

    async def send_method(self, ws, uid, msg):
        fut = asyncio.Future()
        self.awaited_methods[uid] = fut
        self.awaited_method_messages[uid] = msg['params'][0]
        await sock.send(ws, msg)
        return await fut

    def send_method_noblock(self, ws, uid: str, msg: Mapping, callback=None):
        if callback:
            fut: asyncio.Future = asyncio.Future()
            fut.add_done_callback(callback)
            self.awaited_methods[uid] = fut
            self.awaited_method_messages[uid] = msg['params'][0]
        sock.send(ws, msg)

    def recv_result(self, result: Mapping):
        uid = result['id']
        awaited = self.awaited_methods.get(uid)
        if awaited:
            awaited.set_result(result)
            recover_message = self.awaited_method_messages[uid]
            del self.awaited_methods[uid]
            del self.awaited_method_messages[uid]
            if 'error' in result:
                raise ServerException(result, recover_message)

    def recv_ready(self, ready: Mapping):
        uid = ready['subs'][0]
        awaited = self.awaited_subs.get(uid)
        if awaited:
            awaited.set_result(ready)
            del self.awaited_subs[uid]

    def recv(self, msg: Mapping):
        if msg['msg'] == 'result':
            self.recv_result(msg)
        elif msg['msg'] == 'ready':
            self.recv_ready(msg)
