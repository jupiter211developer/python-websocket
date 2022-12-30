import asyncio
import time
import websockets
import pickle
from websockets import WebSocketServerProtocol


class SocketData:
    message = ""
    timestamp = time.time()


class Server:
    clients = []

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.append(ws)
        print(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        print(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str) -> None:
        print(f'send_to_clients {len(self.clients)}')

        data = SocketData()
        data.message = message
        data.timestamp = time.time()
        send_str = pickle.dumps(data)
        send_clients = self.clients[1:]

        if send_clients:
            await asyncio.wait([asyncio.create_task(client.send(send_str)) for client in send_clients])
        if self.clients[0]:
            await self.clients[0].send('received')

        print("take time: ", (int)((time.time() - data.timestamp) * 1000))

    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
        print("------------ws_handler start---------------")
        await self.register(ws)

        try:
            await self.distribute(ws)
        except Exception as e:
            print("**********exception**********", e)
        finally:
            await self.unregister(ws)

        print("------------ws_handler end---------------")

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        print("------------distrubute---------------")
        async for message in ws:
            await self.send_to_clients(message)

# server = Server()
# start_server = websockets.serve(server.ws_handler, 'localhost', 4000)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(start_server)
# loop.run_forever()
