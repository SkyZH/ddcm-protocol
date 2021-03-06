import asyncio
import logging
import unittest
import random

try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair

import ddcm

from .. import const

class TCPRPCTest(unittest.TestCase):
    def get_key_pair(self):
        return bytes(random.getrandbits(8) for i in range(20)), bytes(random.getrandbits(8) for i in range(120))

    def get_reduce_pair(self):
        return bytes(random.getrandbits(8) for i in range(20)), bytes(random.getrandbits(8) for i in range(20)), bytes(random.getrandbits(8) for i in range(120))

    def TestCase(func):
        def _deco(*args, **kwargs):
            config = ddcm.utils.load_config("config.json")

            loop = asyncio.get_event_loop()
            loop.set_debug(config['debug']['asyncio']['enabled'])

            service = ddcm.Service(config, loop)
            echo = ddcm.utils.get_echo_bytes()

            rsock, wsock = socketpair()

            reader, writer = loop.run_until_complete(
                asyncio.open_connection(sock=rsock, loop=loop)
            )

            kwargs = {
                'reader': reader,
                'wsock': wsock,
                'tcpService': service.tcpService,
                'echo': echo,
                'loop': loop
            }

            ret = func(*args, **kwargs)

            writer.close()
            wsock.close()

            return ret
        return _deco

    @TestCase
    def test_pack_ping(self, loop, reader, wsock, tcpService, echo):
        wsock.send(
            tcpService.rpc.pack_ping(
                tcpService.node,
                tcpService.server.remote,
                echo
            )
        )

        _command, _echo, _remoteNode, _data = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.PING)
        self.assertEqual(echo, _echo)

    @TestCase
    def test_pack_pong_ping(self, loop, reader, wsock, tcpService, echo):
        wsock.send(
            tcpService.rpc.pack_pong(
                tcpService.node,
                tcpService.server.remote,
                echo
            )
        )

        _command, _echo, _remoteNode, _data = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.PONG)
        self.assertEqual(echo, _echo)

    @TestCase
    def test_pack_store(self, loop, reader, wsock, tcpService, echo):
        key, value = self.get_key_pair()

        wsock.send(
            tcpService.rpc.pack_store(
                tcpService.node,
                tcpService.server.remote,
                echo,
                key,
                value
            )
        )

        _command, _echo, _remoteNode, (_key, _value) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.STORE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_key, key)
        self.assertEqual(_value, value)

    @TestCase
    def test_pack_pong_store(self, loop, reader, wsock, tcpService, echo):
        key, value = self.get_key_pair()

        wsock.send(
            tcpService.rpc.pack_pong_store(
                tcpService.node,
                tcpService.server.remote,
                echo,
                key
            )
        )

        _command, _echo, _remoteNode, (_key) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.PONG_STORE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_key, key)

    @TestCase
    def test_pack_findNode(self, loop, reader, wsock, tcpService, echo):
        remoteId = ddcm.utils.get_random_node_id()

        wsock.send(
            tcpService.rpc.pack_findNode(
                tcpService.node,
                tcpService.server.remote,
                echo,
                remoteId
            )
        )

        _command, _echo, _remoteNode, (_remoteId) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.FIND_NODE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_remoteId, remoteId)

    @TestCase
    def test_pack_pong_findNode(self, loop, reader, wsock, tcpService, echo):
        remoteId = ddcm.utils.get_random_node_id()
        remoteNodes = [
            ddcm.Node(
                id = ddcm.utils.get_random_node_id(),
                remote = ddcm.Remote(
                    host = "59.48.23.233",
                    port=random.randrange(1, 65534)
                )
            ) for i in range(10)
        ]

        wsock.send(
            tcpService.rpc.pack_pong_findNode(
                tcpService.node,
                tcpService.server.remote,
                echo,
                remoteId,
                remoteNodes
            )
        )

        _command, _echo, _remoteNode, (_remoteId, _remoteNodeCount, _remoteNodes) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.PONG_FIND_NODE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_remoteId, remoteId)
        self.assertEqual(_remoteNodeCount, len(remoteNodes))
        for i in range(len(remoteNodes)):
            self.assertEqual(_remoteNodes[i].id, remoteNodes[i].id)
            self.assertEqual(_remoteNodes[i].remote.host, remoteNodes[i].remote.host)
            self.assertEqual(_remoteNodes[i].remote.port, remoteNodes[i].remote.port)

    @TestCase
    def test_pack_findValue(self, loop, reader, wsock, tcpService, echo):
        key, value = self.get_key_pair()

        wsock.send(
            tcpService.rpc.pack_findValue(
                tcpService.node,
                tcpService.server.remote,
                echo,
                key
            )
        )

        _command, _echo, _remoteNode, (_key) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.FIND_VALUE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_key, key)

    @TestCase
    def test_pack_pong_findValue(self, loop, reader, wsock, tcpService, echo):
        key, value = self.get_key_pair()

        wsock.send(
            tcpService.rpc.pack_pong_findValue(
                tcpService.node,
                tcpService.server.remote,
                echo,
                key,
                value
            )
        )

        _command, _echo, _remoteNode, (_key, _value) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.PONG_FIND_VALUE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_key, key)
        self.assertEqual(_value, value)

    @TestCase
    def test_pack_reduce(self, loop, reader, wsock, tcpService, echo):
        keyS, keyE, value = self.get_reduce_pair()

        wsock.send(
            tcpService.rpc.pack_reduce(
                tcpService.node,
                tcpService.server.remote,
                echo,
                keyS,
                keyE
            )
        )

        _command, _echo, _remoteNode, (_keyS, _keyE) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.REDUCE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_keyS, keyS)
        self.assertEqual(_keyE, keyE)

    @TestCase
    def test_pack_pong_reduce(self, loop, reader, wsock, tcpService, echo):
        keyS, keyE, value = self.get_reduce_pair()

        wsock.send(
            tcpService.rpc.pack_pong_reduce(
                tcpService.node,
                tcpService.server.remote,
                echo,
                keyS,
                keyE,
                value
            )
        )

        _command, _echo, _remoteNode, (_keyS, _keyE, _value) = loop.run_until_complete(
            asyncio.ensure_future(
                tcpService.rpc.read_command(reader)
            )
        )

        self.assertEqual(_command, ddcm.const.kad.command.PONG_REDUCE)
        self.assertEqual(_echo, echo)
        self.assertEqual(_keyS, keyS)
        self.assertEqual(_keyE, keyE)
        self.assertEqual(_value, value)
