import struct
import json
import socket

from .. import const

from ..Remote import Remote
from ..Node import Node

class TCPRPC(object):
    def __init__(self, service, loop):
        self.service = service
        self.loop = loop

    def pack_ping(self, local, remote, echo):
        """Pack Ping Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.PING),
            echo,
            local.id,
            self.pack_remote(remote)
        ])

    def pack_pong(self, local, remote, echo):
        """Pack Ping Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Recieved Echo Message

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.PONG),
            echo,
            local.id,
            self.pack_remote(remote)
        ])

    async def read_ping(self, reader):
        return None
    async def read_pong(self, reader):
        return None

    def pack_store(self, local, remote, echo, key, value):
        """Pack FindNode Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message
            key, value: (key, value) to save

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.STORE),
            echo,
            local.id,
            self.pack_remote(remote),
            key,
            struct.pack('>L', len(value)),
            value
        ])

    def pack_pong_store(self, local, remote, echo, key):
        """Pack Pong Store Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Recieved Echo Message
            key: Key Saved

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.PONG_STORE),
            echo,
            local.id,
            self.pack_remote(remote),
            key
        ])

    async def read_store(self, reader):
        key = await reader.readexactly(20)
        len_value = struct.unpack('>L', await reader.readexactly(4))[0]
        value = await reader.readexactly(len_value)
        return key, value

    async def read_pong_store(self, reader):
        key = await reader.readexactly(20)
        return key

    def pack_findNode(self, local, remote, echo, remoteId):
        """Pack FindNode Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message
            remoteId: Hash of Node to Ping

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.FIND_NODE),
            echo,
            local.id,
            self.pack_remote(remote),
            remoteId
        ])

    def pack_pong_findNode(self, local, remote, echo, remoteId, remoteNodes):
        """Pack Pong FindNode Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message
            remoteId: Hash of Node to return
            remoteNode: Remote Address
        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.PONG_FIND_NODE),
            echo,
            local.id,
            self.pack_remote(remote),
            remoteId,
            struct.pack('B', len(remoteNodes)),
            *[
                self.pack_node(remoteNode) for remoteNode in remoteNodes
            ]
        ])

    async def read_findNode(self, reader):
        return await reader.readexactly(20)

    async def read_pong_findNode(self, reader):
        remoteId = await reader.readexactly(20)
        remoteCount = struct.unpack('B', await reader.readexactly(1))[0]
        remoteNodes = []
        for i in range(remoteCount):
            remoteNodes.append(await self.read_node(reader))
        return remoteId, remoteCount, remoteNodes

    def pack_findValue(self, local, remote, echo, key):
        """Pack FindValue Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message
            key: Key to Find

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.FIND_VALUE),
            echo,
            local.id,
            self.pack_remote(self.service.server.remote),
            key
        ])

    def pack_pong_findValue(self, local, remote, echo, key, value):
        """Pack Pong FindValue Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message
            key, value: (key, value) to send

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.PONG_FIND_VALUE),
            echo,
            local.id,
            self.pack_remote(self.service.server.remote),
            key,
            struct.pack('>L', len(value)),
            value
        ])

    async def read_findValue(self, reader):
        key = await reader.readexactly(20)
        return key

    async def read_pong_findValue(self, reader):
        key = await reader.readexactly(20)
        len_value = struct.unpack('>L', await reader.readexactly(4))[0]
        value = await reader.readexactly(len_value)
        return key, value

    def pack_reduce(self, local, remote, echo, keyStart, keyEnd):
        """Pack FindValue Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message
            keyStart, keyEnd: Keys to Reduce

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.REDUCE),
            echo,
            local.id,
            self.pack_remote(self.service.server.remote),
            keyStart,
            keyEnd
        ])

    def pack_pong_reduce(self, local, remote, echo, keyStart, keyEnd, value):
        """Pack Pong FindValue Message

        Args:
            local: Self Node
            remote: Self Address
            echo: Random Echo Message
            key, value: (key, value) to send
            keyStart, keyEnd: Keys to Reduce

        Returns:
            Packed Data to Send
        """
        return b"".join([
            struct.pack('B', const.kad.command.PONG_REDUCE),
            echo,
            local.id,
            self.pack_remote(self.service.server.remote),
            keyStart,
            keyEnd,
            struct.pack('>L', len(value)),
            value
        ])

    async def read_reduce(self, reader):
        keyStart = await reader.readexactly(20)
        keyEnd = await reader.readexactly(20)
        return keyStart, keyEnd

    async def read_pong_reduce(self, reader):
        keyStart = await reader.readexactly(20)
        keyEnd = await reader.readexactly(20)
        len_value = struct.unpack('>L', await reader.readexactly(4))[0]
        value = await reader.readexactly(len_value)
        return keyStart, keyEnd, value

    def get_command_string(self, id):
        return const.kad.command.COMMANDS[id]

    def pack_remote(self, remote):
        remote_ip = socket.inet_aton(remote.host)
        return b"".join([
            struct.pack('>BH', len(remote_ip), remote.port),
            remote_ip
        ])

    async def read_remote(self, reader):
        ip_size, port = struct.unpack('>BH', await reader.readexactly(3))
        host = socket.inet_ntoa(await reader.readexactly(ip_size))
        return Remote(
            host = host,
            port = port
        )

    def pack_node(self, node):
        return b"".join([
            node.id,
            self.pack_remote(node.remote)
        ])

    async def read_node(self, reader):
        node = Node(
            await reader.readexactly(20),
            remote = await self.read_remote(reader)
        )
        return node

    async def read_command(self, reader):
        """Read Command

        Args:
            reader: a StreamReader object

        Returns:
            JSON Data
        """
        command = struct.unpack('B', await reader.readexactly(1))[0]
        echo = await reader.readexactly(20)
        remoteNode = Node(
            id = await reader.readexactly(20),
            remote = await self.read_remote(reader)
        )
        data = (command, echo, remoteNode)
        if command is const.kad.command.PING:
            return (*data, await self.read_ping(reader))
        elif command is const.kad.command.PONG:
            return (*data, await self.read_pong(reader))
        elif command is const.kad.command.STORE:
            return (*data, await self.read_store(reader))
        elif command is const.kad.command.PONG_STORE:
            return (*data, await self.read_pong_store(reader))
        elif command is const.kad.command.FIND_NODE:
            return (*data, await self.read_findNode(reader))
        elif command is const.kad.command.PONG_FIND_NODE:
            return (*data, await self.read_pong_findNode(reader))
        elif command is const.kad.command.FIND_VALUE:
            return (*data, await self.read_findValue(reader))
        elif command is const.kad.command.PONG_FIND_VALUE:
            return (*data, await self.read_pong_findValue(reader))
        elif command is const.kad.command.REDUCE:
            return (*data, await self.read_reduce(reader))
        elif command is const.kad.command.PONG_REDUCE:
            return (*data, await self.read_pong_reduce(reader))
