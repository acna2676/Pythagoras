import time

import save_db

if __name__ == '__main__':
    start = time.time()
    save_db.lambda_handler(None, None)
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
