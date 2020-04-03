import logging
import random
import threading
import time

from basic_loging_configuration import initialize_logging

initialize_logging()
semaphore = threading.Semaphore(0)


def consumer():
    logging.info("Consumer is waiting")
    semaphore.acquire()
    logging.info(f"Consumer now has value {item}")


def producer():
    global item
    time.sleep(1)
    item = random.randint(0, 1000)
    logging.info(f"Producer notify: Produced item number {item}")
    semaphore.release()


if __name__ == '__main__':
    for i in range(0, 5):
        t1 = threading.Thread(target=producer)
        t2 = threading.Thread(target=consumer)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    logging.info("Program terminated")
