import logging
import sys
import threading

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(threadName)s (%(levelname)s): #%(lineno)d %(message)s'
)


shared_resource_with_lock = 0
shared_resource_with_no_lock = 0
shared_resource_lock = threading.Lock()
COUNT = 100000


def increment_with_lock():
    global shared_resource_with_lock
    for i in range(COUNT):
        shared_resource_lock.acquire()
        shared_resource_with_lock += 1
        shared_resource_lock.release()


def decrement_with_lock():
    global shared_resource_with_lock
    for i in range(COUNT):
        shared_resource_lock.acquire()
        shared_resource_with_lock -= 1
        shared_resource_lock.release()


# No locking below
def increment_with_no_lock():
    global shared_resource_with_no_lock
    for i in range(COUNT):
        shared_resource_with_no_lock += 1


def decrement_with_no_lock():
    global shared_resource_with_no_lock
    for i in range(COUNT):
        shared_resource_with_no_lock -= 1


if __name__ == '__main__':
    t1 = threading.Thread(name="increment_with_lock",
                          target=increment_with_lock)
    t2 = threading.Thread(name="decrement_with_lock",
                          target=decrement_with_lock)
    t3 = threading.Thread(name="increment_with_no_lock",
                          target=increment_with_no_lock)
    t4 = threading.Thread(name="decrement_with_no_lock",
                          target=decrement_with_no_lock)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()

    logging.info(f"The value of variable with lock management is "
                 f"{shared_resource_with_lock}")
    logging.info(f"The value of variable with no lock management is "
                 f"{shared_resource_with_no_lock}")
