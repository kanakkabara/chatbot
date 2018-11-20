#!/usr/bin/env python3

from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.styles import style_from_dict
import prompt_toolkit.shortcuts
from prompt_toolkit.shortcuts import create_prompt_application, create_asyncio_eventloop, prompt_async
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
import sys

import logging
import importlib
logging.basicConfig(level='ERROR')
import concurrent
import asyncio
import unha2.client as client
from unha2.model.base import RoomType
from unha2.methods import MethodError
from bot import response

eventloop = create_asyncio_eventloop()
cli = CommandLineInterface(
    application=create_prompt_application('> '),
    eventloop=eventloop)
sys.stdout = cli.stdout_proxy()

STYLE_DICT = {
    Token.Title: 'bold',
    Token.Error: '#ansired',
    Token.Nick: '#ansiyellow',
    Token.Server: '#ansiblue',
    Token.Chat: '#ansigreen',
    Token.Direct: '#ansifuchsia',
    Token.Private: '#ansiblue',
    Token.Time: '#ansilightgray',
    Token.Separator: '#ansilightgray bold',
}

STYLE = style_from_dict(STYLE_DICT)

def cmd(n):
    def wrapper(func):
        def inner(self, args=None):
            if args is None and n == 0:
                func(self)
                return
            spl = args.split(' ', maxsplit=n)
            if len(spl) != n:
                print('Wrong args')
                return False
            else:
                func(self, *spl)
        return inner
    return wrapper

def print_cli(tokens):
    cli.run_in_terminal(lambda: cli.print_tokens(tokens, style=STYLE))

def print_error(payload):
    err = payload.get('error')
    if not err or not err.get('message'):
        return
    tokens = [
        (Token.Error, 'Error: '),
        (Token, err['message']),
        (Token, '\n')
    ]
    print_cli(tokens)

def print_login(username, server):
    tokens = [
        (Token.Title, 'Logged in as '),
        (Token.Nick, username),
        (Token.Title, ' on '),
        (Token.Server, server),
        (Token, '\n')
    ]
    print_cli(tokens)

async def interactive_shell(client):
    while True:
        try:
            client.on_input((await cli.run_async()).text)
        except (EOFError, KeyboardInterrupt):
            return

async def print_rooms(coro):
    results = await coro
    private = []
    direct = []
    chat = []
    for result in results['update']:
        if result['type'] == RoomType.DIRECT:
            direct.append(result['name'])
        elif result['type'] == RoomType.PRIVATE:
            private.append(result['name'])
        elif result['type'] == RoomType.CHAT:
            chat.append(result['name'])
    chat.sort()
    private.sort()
    direct.sort()

    tok = []
    if chat:
        tok2 = [(Token.Title, 'Public chats:'), (Token, '\n')]
        for room in chat:
            add = [(Token, ' '), (Token.Chat, room), (Token, '\n')]
            tok2.extend(add)
        tok.extend(tok2)
    if private:
        tok2 = [(Token.Title, 'Private groups:'), (Token, '\n')]
        for room in private:
            add = [(Token, ' '), (Token.Private, room), (Token, '\n')]
            tok2.extend(add)
        tok.extend(tok2)
    if direct:
        tok2 = [(Token.Title, 'Direct chats:'), (Token, '\n')]
        for room in direct:
            add = [(Token, ' '), (Token.Direct, room), (Token, '\n')]
            tok2.extend(add)
        tok.extend(tok2)

    print_cli(tok)

class FreetalkLike(client.OverrideClient):
    def __init__(self, server, user, password):
        client.OverrideClient.__init__(self, server, user, password)
        self.room_map = {}
        self.name_map = {}
        self.type_map = {}

    async def make_new_room_and_add_user(self, name, user_id):
        if name in self.name_map:
            print("Room with given name already exists please try a different name")
        else:
            result = await self.api.make_room_and_add_user(name, [user_id.name])
            self.room_map[result['result']['rid']] = name
            self.name_map[name] = result['result']['rid']
            self.api.subscribe_to_room({"room_id": result['result']['rid']})
            self.api.send_msg(result['result']['rid'], "Hey "+ user_id.name + " welcome to your personalised advisory bot!")


    async def get_id(self, name):
        if name in self.name_map:
            return self.name_map[name]
        else:
            result = await self.api.get_room_id(name)
            if 'room_id' in result:
                self.room_map[result['room_id']] = name
                self.name_map[name] = result['room_id']
                return result['room_id']

    async def do_login(self):
        try:
            await super().do_login()
        except MethodError as e:
            print_error(e.args[0])
            self.stop = True
            return

        print_login(self.data.username, self.data.server)
        rooms = await self.api.get_subscriptions()
        self.api.subscribe_user_all()
        for room in rooms['update']:
            self.type_map[room['room_id']] = room['type']
            self.room_map[room['room_id']] = room['name']
            self.name_map[room['name']] = room['room_id']
            self.api.subscribe_to_room(room)

    def on_input(self, text):
        self.command_parser(text)

    @cmd(0)
    def cmd_rooms(self):
        asyncio.ensure_future(print_rooms(self.api.get_subscriptions()))

    @cmd(0)
    def cmd_help(self):
        tokens = [
            (Token.Title, 'Commands:\n'),
            (Token, ' say <room-name> <message>\n'),
            (Token, ' join <room-name>\n'),
            (Token, ' leave <room-name>\n'),
            (Token, ' show <room-name> <number-of-messages>\n'),
            (Token, ' rooms\n'),
        ]
        print_cli(tokens)

    async def join(self, room_name):
        room_id = await self.get_id(room_name)
        result = await self.api.join_room(room_id)
        print_error(result)

    async def leave(self, room_name):
        room_id = await self.get_id(room_name)
        result = await self.api.leave_room(room_id)
        print_error(result)

    @cmd(1)
    def cmd_join(self, room_name):
        asyncio.ensure_future(self.join(room_name))

    @cmd(1)
    def cmd_leave(self, room_name):
        asyncio.ensure_future(self.leave(room_name))

    @cmd(2)
    def cmd_show(self, room_name, number):
        try:
            number = int(number)
        except ValueError:
            print('Wrong number of messages')
            number = 5
        asyncio.ensure_future(self.show(room_name, number))

    async def show(self, room_name, number):
        try:
            room_id = await self.get_id(room_name)
            results = await self.api.load_history(room_id, None, number)
        except MethodError as e:
            print_error(e.args[0])
            return
        toks = []
        for result in results:
            res = super().on_room_message(result)
            if res:
                toks.extend(res)
        print_cli(toks)

    @cmd(2)
    def cmd_say(self, room, msg):
        self.api.send_msg(self.name_map[room], msg)

    def command_parser(self, line):
        if not line.strip():
            return

        handlers = {
            'rooms': self.cmd_rooms,
            'join': self.cmd_join,
            'say': self.cmd_say,
            'leave': self.cmd_leave,
            'show': self.cmd_show,
            'help': self.cmd_help,
            '': lambda: None
        }
        com, *remainder = line.split(' ', maxsplit=1)
        if com in handlers:
            if com=="send":
                room, *message = remainder[0].split(' ', maxsplit=1)
                self.api.send_msg(self.name_map[room], message[0])
            elif remainder:
                handlers[com](remainder[0])
            else:
                handlers[com]()
        else:
            print('unknown command')

    def room_build(self, room_id, time, content_tokens):
        tokens = []
        room_type = self.type_map.get(room_id, RoomType.CHAT)
        if room_type == RoomType.DIRECT:
            tokens.append((Token.Direct, self.room_map[room_id]))
        elif room_type == RoomType.PRIVATE:
            tokens.append((Token.Private, self.room_map[room_id]))
        elif room_type == RoomType.CHAT:
            tokens.append((Token.Chat, self.room_map[room_id]))
        tokens.append((Token, ' '))
        tokens.append((Token.Time, time.strftime('%H:%M:%S')))
        tokens.extend(content_tokens)
        tokens.append((Token, '\n'))
        return tokens

    def on_user_joined(self, msg):
        toks = [(Token.Separator, ' - '), (Token.Nick, msg['user'].name), (Token, ' joined the room')]
        asyncio.ensure_future((self.make_new_room_and_add_user(msg['user'].name+"_advisory_bot", msg['user'])))
        return self.room_build(msg['room_id'], msg['creation_time'], toks)

    def on_user_left(self, msg):
        toks = [(Token.Separator, ' - '), (Token.Nick, msg['user'].name), (Token, ' left the room')]
        return self.room_build(msg['room_id'], msg['creation_time'], toks)

    def on_normal_message(self, msg):
        content = [(Token.Separator, ' | '), (Token.Nick, msg['user'].name), (Token, '> %s' % msg['msg'])]
        if msg.get('attachments'):
            for att in msg['attachments']:
                content.append((Token, '\n %s - %s' % (att.get('author_link', ''), att.get('author_name', ''))))
        if self.room_map[msg['room_id']] != 'general' and msg['user'].name != 'roncool':
            response_message, _ = response(msg['msg'], msg['user'].name)
            self.api.send_msg(msg['room_id'], response_message)
        return self.room_build(msg['room_id'], msg['creation_time'], content)

    async def on_room_message(self, msg):
        toks = super().on_room_message(msg)
        print_cli(toks)

def main():
    client = FreetalkLike("simpleserver.ga", "roncool", "password")
    loop = asyncio.get_event_loop()
    shell_task = loop.create_task(interactive_shell(client))
    handler_task = loop.create_task(client.handler_loop())
    network_task = loop.create_task(client.network_loop(loop))

    loop.run_until_complete(asyncio.wait([shell_task, handler_task, network_task], return_when=concurrent.futures.FIRST_COMPLETED))
    shell_task.cancel()
    handler_task.cancel()
    network_task.cancel()
    loop.close()


if __name__ == '__main__':
    main()

