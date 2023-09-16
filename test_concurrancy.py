import multiprocessing
import threading
import asyncio

# Example function to run as an asyncio task
async def async_task(task_id):
    print(f"Async task {task_id} started")
    await asyncio.sleep(1)
    print(f"Async task {task_id} completed")

# Example function to run as a thread
def thread_function(thread_id):
    print(f"Thread {thread_id} started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(asyncio.gather(
        async_task(f"Task 1 in Thread {thread_id}"),
        async_task(f"Task 2 in Thread {thread_id}")
    ))
    print(f"Thread {thread_id} completed")

# Example function to run as a process
def process_function(process_id):
    print(f"Process {process_id} started")
    threads = []
    for i in range(2):
        thread = threading.Thread(target=thread_function, args=(f"Thread {i} in Process {process_id}",))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print(f"Process {process_id} completed")

if __name__ == '__main__':
    processes = []
    for i in range(multiprocessing.cpu_count()):
        process = multiprocessing.Process(target=process_function, args=(f"Process {i}",))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
