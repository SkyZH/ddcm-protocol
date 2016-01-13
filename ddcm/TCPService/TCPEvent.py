from .. import const

class TCPEvent(object):
    """TCPEvent
    Handle TCP Events
    """
    def __init__(self, loop, service):
        self.loop = loop
        self.service = service
        self.enabled = self.service.config["debug"]["events"]

    async def add_event(self, event_type, data = None):
        if self.enabled:
            await self.service.queue.put({
                "service": const.kad.event.TCPService,
                "type": event_type,
                "data": data
            })

    async def do_pong_ping(self, remote, echo):
        await self.add_event(const.kad.event.SEND_PONG_PING, {
            "remote": remote,
            "echo": echo
        })
    async def do_ping(self, remote, echo):
        await self.add_event(const.kad.event.SEND_PING, {
            "remote": remote,
            "echo": echo
        })
    async def handle_pong_ping(self, echo, remoteNode, data):
        await self.add_event(const.kad.event.HANDLE_PONG_PING, {
            "remoteNode": remoteNode,
            "echo": echo,
            "data": data
        })
    async def handle_ping(self, echo, remoteNode, data):
        await self.add_event(const.kad.event.HANDLE_PING, {
            "remoteNode": remoteNode,
            "echo": echo,
            "data": data
        })

    async def do_pong_store(self, remote, echo, key):
        await self.add_event(const.kad.event.SEND_PONG_STORE, {
            "remote": remote,
            "echo": echo,
            "data": (key)
        })
    async def do_store(self, remote, echo, key, value):
        await self.add_event(const.kad.event.SEND_STORE, {
            "remote": remote,
            "echo": echo,
            "data": (key, value)
        })
    async def handle_pong_store(self, echo, remoteNode, data):
        await self.add_event(const.kad.event.HANDLE_PONG_STORE, {
            "remoteNode": remoteNode,
            "echo": echo,
            "data": data
        })
    async def handle_store(self, echo, remoteNode, data):
        await self.add_event(const.kad.event.HANDLE_STORE, {
            "remoteNode": remoteNode,
            "echo": echo,
            "data": data
        })
