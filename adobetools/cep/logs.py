'''

logs land in: ~/Library/Logs/CSXS

look like:
    CEPHtmlEngine7-PHXS-17.0.1-com.mminternals.mmphotoshop.main.log
    CEPHtmlEngine7-PHXS-17.0.1-com.mminternals.mmphotoshop.main-renderer.log
    CEPHtmlEngine6-PPRO-11.0.0-com.mminternals.mm52x2.main.log

stats
-----
first
    436207619 3734445 -rwxrwxr-x 1 mikeb cg 0 9041 "Oct  2 09:42:19 2017" "Oct  2 09:42:19 2017" "Oct  2 09:42:19 2017" "Dec 31 19:00:00 1969" 1048576 18 0 CEPHtmlEngine7-PHXS-17.0.1-com.mminternals.mmphotoshop.main.log
log from the panel
    436207619 3734445 -rwxrwxr-x 1 mikeb cg 0 9222 "Oct  2 09:42:19 2017" "Oct  2 09:43:02 2017" "Oct  2 09:43:02 2017" "Dec 31 19:00:00 1969" 1048576 19 0 CEPHtmlEngine7-PHXS-17.0.1-com.mminternals.mmphotoshop.main.log
again
    436207619 3734445 -rwxrwxr-x 1 mikeb cg 0 9403 "Oct  2 09:42:19 2017" "Oct  2 09:44:35 2017" "Oct  2 09:44:35 2017" "Dec 31 19:00:00 1969" 1048576 19 0 CEPHtmlEngine7-PHXS-17.0.1-com.mminternals.mmphotoshop.main.log
close the panel
    436207619 3734445 -rwxrwxr-x 1 mikeb cg 0 43948 "Oct  2 09:42:19 2017" "Oct  2 09:44:59 2017" "Oct  2 09:44:59 2017" "Dec 31 19:00:00 1969" 1048576 86 0 CEPHtmlEngine7-PHXS-17.0.1-com.mminternals.mmphotoshop.main.log
open the panel
    436207619 3734445 -rwxrwxr-x 1 mikeb cg 0 9041 "Oct  2 09:42:19 2017" "Oct  2 09:45:12 2017" "Oct  2 09:45:12 2017" "Dec 31 19:00:00 1969" 1048576 18 0 CEPHtmlEngine7-PHXS-17.0.1-com.mminternals.mmphotoshop.main.log
        it truncated!


'''


import argparse
import os
import sys
import threading
import time


MIN_DELAY = 0.05
MAX_DELAY = 1.00


def target(path):
    
    name = os.path.basename(path)
    delay = MIN_DELAY

    fh = open(path)

    while True:
        
        line = fh.readline().rstrip()
        if line:
            sys.stdout.write('[{}] {}\n'.format(name, line))
            sys.stdout.flush()
            delay = 0
            continue

        if fh.tell() > os.stat(path).st_size:
            sys.stdout.write('[{}] RESET'.format(name))
            sys.stdout.flush()
            fh.seek(0)
            continue

        time.sleep(delay)
        delay = min(MAX_DELAY, max(MIN_DELAY, 2 * delay))


def create_threads(dir_, pool, internal=False):
    for name in os.listdir(dir_):

        if name in pool:
            continue

        if (not internal) and 'adobe' in name:
            pool[name] = None
            continue

        path = os.path.join(dir_, name)
        thread = threading.Thread(target=target, args=[path])
        thread.daemon = True
        thread.start()
        pool[name] = thread


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', default=os.path.expanduser('~/Library/Logs/CSXS'))
    parser.add_argument('-i', '--internal', action='store_true')
    args = parser.parse_args()

    pool = {}
    while True:
        create_threads(args.dir, pool, internal=args.internal)
        time.sleep(1)


if __name__ == '__main__':
    main()

    