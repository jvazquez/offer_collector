import concurrent.futures
import logging
import time

from utils.basic_loging_configuration import initialize_logging

initialize_logging()

number_list = list(range(1, 11))


def count(number):
    for i in range(0, 10000000):
        i = i+1
    return i * number


def evaluate_item(x):
    result_item = count(x)
    logging.info(f"Item {x}: result:{result_item}")


if __name__ == '__main__':
    start_time = time.clock()
    for item in number_list:
        evaluate_item(item)
        logging.info(f"Sequential execution in {time.clock() - start_time}")
        start_time_one = time.clock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for item in number_list:
            executor.submit(evaluate_item, item)
        logging.info(f"Threadpool execution in "
                     f"{time.clock() - start_time_one} seconds")

    start_time_two = time.clock()
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        for item in number_list:
            executor.submit(evaluate_item, item)
        logging.info(f"ProcessPool execution in "
                     f"{time.clock() - start_time_two} seconds")
