import threading
import queue


def threaded(func):
    """A decorator to run a function in a new thread."""

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def threaded_value(func):
    """A decorator to run a function in a new thread and retrieve its return value."""

    def wrapper(*args, **kwargs):
        q = queue.Queue()

        def inner_func(*args, **kwargs):
            result = func(*args, **kwargs)
            q.put(result)

        thread = threading.Thread(target=inner_func, args=args, kwargs=kwargs)
        thread.start()
        thread.join()  # Wait for the thread to complete
        return q.get()  # Retrieve the result

    return wrapper
