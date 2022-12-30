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


def add_to_queue(path, readtime, delaytime, common_queue):
    old_out = sys.stdout
    sys.stdout = open('[log] - generate.txt', 'w')

    line_count = 0
    last_read = time.time()
    with open(path, "r") as f:
        while True:
            line = f.readline()
            line_count += 1
            curr_time = time.time()

            if curr_time - last_read > readtime * 1000 or not line:
                print(
                    "Read {} lines in {} seconds".format(
                        line_count, curr_time - last_read
                    ),
                    flush=True,
                )
                line_count = 0
                print("sleeping for {} seconds".format(delaytime), flush=True)
                time.sleep(delaytime)
                print("done sleeping", flush=True)
                last_read = time.time()
            if not line:
                break
            common_queue.put(line)

        print("Done reading file", flush=True)

    sys.stdout = old_out


async def send_data(common_queue):
    print("-----------send data------------")
    try:
        async with websockets.connect('ws://127.0.0.1:4000') as websocket:
            while 1:
                try:
                    msg = common_queue.get()
                    await websocket.send(msg)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


def read_from_queue(delaytime, common_queue):
    time.sleep(delaytime)
    asyncio.run(send_data(common_queue))


if __name__ == "__main__":
    print("---------------------------WEBSOCKET POC---------------------------")

    manager = multiprocessing.Manager()
    common_queue = manager.Queue()

    creator_process = multiprocessing.Process(
        target=create_server, args=[]
    )
    feed_feeder_process = multiprocessing.Process(
        target=add_to_queue, args=["data.csv", 1, 1, common_queue]
    )
    feed_reader_process = multiprocessing.Process(
        target=read_from_queue, args=[3, common_queue]
    )
    generate_client_process = multiprocessing.Process(
        target=generate_clients, args=[5, 1]
    )
    process_list = [creator_process, feed_feeder_process, feed_reader_process, generate_client_process]
    for p in process_list:
        p.start()

    for p in process_list:
        p.join()
