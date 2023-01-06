import time
import multiprocessing
import websockets
import asyncio
import sys
from server import Server
from client import generate_clients

# websocket server


def create_server():
    old_out = sys.stdout
    sys.stdout = open('[log] - server.txt', 'w')

    server = Server()
    start_server = websockets.serve(server.ws_handler, 'localhost', 4000)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()

    sys.stdout = old_out

# data receive


def add_to_queue(delaytime, common_queue):
    while True:
        time.sleep(0.05)
        print("done sleeping", flush=True)
        common_queue.put(1)


async def send_data(common_queue, path):
    try:
        async with websockets.connect('ws://127.0.0.1:4000') as websocket:
            f = open(path, "r")
            msg = f.read()
            f.close()
            while 1:
                try:
                    common_queue.get()
                    print("send a message to server")
                    await websocket.send(msg)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


def read_from_queue(delaytime, common_queue, path):
    time.sleep(delaytime)
    asyncio.run(send_data(common_queue, path))


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    common_queue = manager.Queue()

    creator_process = multiprocessing.Process(
        target=create_server, args=[]
    )
    feed_feeder_process = multiprocessing.Process(
        target=add_to_queue, args=[1, common_queue]
    )
    feed_reader_process = multiprocessing.Process(
        target=read_from_queue, args=[3, common_queue, "500KB.txt"]
    )
    generate_client_process = multiprocessing.Process(
        target=generate_clients, args=[5, 350]
    )
    process_list = [creator_process, feed_feeder_process, feed_reader_process, generate_client_process]
    for p in process_list:
        p.start()

    for p in process_list:
        p.join()
