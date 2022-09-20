import time

import functions.lambda_function as lambda_function

if __name__ == '__main__':
    start = time.time()
    lambda_function.lambda_handler(None, None)
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
