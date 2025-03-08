import threading
import queue

# A global task queue for scheduling actions.
task_queue = queue.Queue()

def task_worker():
    while True:
        func, args = task_queue.get()
        if func is None:
            break
        
        if (isinstance(args, tuple)):
            func(*args)
        else:
            func(args)
            
        task_queue.task_done()

# Start a background worker thread.
worker_thread = threading.Thread(target=task_worker, daemon=True)
worker_thread.start()

def add_task(func, args):
    task_queue.put((func, args))
