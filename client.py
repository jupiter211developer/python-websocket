import asyncio
import websockets
import time
import random
import pickle
import sys


async def produce(index: int, host: str, port: int) -> None:
    total = random.randint(100, 1000000)
    while 1:
        async with websockets.connect(f"ws://{host}:{port}") as ws:
            counter = 0
            while 1:
                counter = counter + 1

                if counter > total:
                    break
                msg = await ws.recv()
                data = pickle.loads(msg)
                cur_time = time.time()
                # print(f'{index}th client => transfer_time: {cur_time - data.timestamp}, message: {data.message}')
                print(f'{index}th client => transfer_time: {(int)((cur_time - data.timestamp) * 1000)}ms')
            ws.close()


async def run_clients(num=100) -> None:
    await asyncio.wait([asyncio.create_task(produce(index=i, host='localhost', port=4000)) for i in range(num)])


def generate_clients(delaytime, num=100) -> None:
    old_out = sys.stdout
    sys.stdout = open('[log] - client.txt', 'w')

    time.sleep(delaytime)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_clients(num))

    sys.stdout = old_out
