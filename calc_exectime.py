import time

import articles_crowler.articles_crowler as articles_crowler

if __name__ == '__main__':
    start = time.time()
    articles_crowler.lambda_handler(None, None)
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
