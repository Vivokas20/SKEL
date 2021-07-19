#!/usr/bin/python

import argparse
import csv
import glob
import os
import pathlib
import re
import subprocess
import random
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Util for benchmarking the SQUARES program synthesizer.')
parser.add_argument('-t', default=600, type=int, help='timeout')
parser.add_argument('-m', default=57344, type=int, help='memout')
parser.add_argument('-n', default=1, type=int, help='number of times to run each instance')
parser.add_argument('-p', default=1, type=int, help='#processes')
parser.add_argument('--append', action='store_true', help='append to file')
parser.add_argument('--cubes', action='store_true', help='use cubes')
parser.add_argument('--portfolio', action='store_true', help='use portfolio')
parser.add_argument('--portfolio2', action='store_true', help='use portfolio 2')
parser.add_argument('--sequential2', action='store_true', help='use sequential 2')
parser.add_argument('--resume', action='store_true', help='resume previous run')
parser.add_argument('--sample', type=float)
parser.add_argument('--instances')
parser.add_argument('name', metavar='NAME', help="name of the result file")

args, other_args = parser.parse_known_args()


def test_file(filename: str, run: str = ''):
    test_name = filename.replace('tests/', '', 1).replace('.yaml', '')
    out_file = f'evaluation/data/{args.name}/{test_name}{run}.log'
    pathlib.Path(os.path.dirname(out_file)).mkdir(parents=True, exist_ok=True)

    if args.cubes:
        command = ['helper-scripts/runsolver', '-W', str(args.t), '--rss-swap-limit', str(args.m), '-d', '5', '-o', out_file, './cubes.py', '-vv', filename]
    elif args.portfolio:
        command = ['helper-scripts/runsolver', '-W', str(args.t), '--rss-swap-limit', str(args.m), '-d', '5', '-o', out_file, './portfolio.py', '-vv', filename]
    elif args.portfolio2:
        command = ['helper-scripts/runsolver', '-W', str(args.t), '--rss-swap-limit', str(args.m), '-d', '5', '-o', out_file, './portfolio2.py', '-vv', filename]
    elif args.sequential2:
        command = ['helper-scripts/runsolver', '-W', str(args.t), '--rss-swap-limit', str(args.m), '-d', '5', '-o', out_file, './sequential2.py', '-vv', filename]
    else:       # This one!
        command = ['helper-scripts/runsolver', '-W', str(args.t), '--rss-swap-limit', str(args.m), '-d', '5', '-o', out_file, 'python3', 'sequential.py', '-vv', filename]

    command += other_args

    print(' '.join(command))
    p = subprocess.run(command, capture_output=True, encoding='utf8')

    timeout = re.search('Maximum wall clock time exceeded: sending SIGTERM then SIGKILL', p.stdout) is not None
    memout = re.search('Maximum memory exceeded: sending SIGTERM then SIGKILL', p.stdout) is not None

    try:
        status = re.search('Child status: (.*)', p.stdout)[1]
    except:
        status = None if timeout or memout else 0

    programs = None
    gt = False
    gt_status = 0
    if not timeout and not memout:
        with open(out_file) as f:
            log = f.read()
            try:
                programs = int(re.search('\tAttempted programs: (.*) \(approx\)', log)[1])
            except:
                programs = None

            try:
                file_solution = re.search('Solution found: \[(.+)]', log)[0]
                file_solution = file_solution.replace("Solution found: ", "")[1:-1]
                file_select = re.search('out <- df[0-9]+ %>% select(.+)', log)[0]
                file_select = file_select.split("%>% ", 1)[1]

                l_name = "evaluation/data/Full/" + filename[:-5] + "_0.log"

                with open(l_name) as l:
                    log_solution = l.read()
                gt_solution = re.search('Solution found: \[(.+)]', log_solution)[0]
                gt_solution = gt_solution.replace("Solution found: ", "")[1:-1]
                select = re.search('out <- df[0-9]+ %>% select(.+)', log_solution)[0]
                select = select.split("%>% ", 1)[1]

                if gt_solution == file_solution:
                    gt = True
                    if select == file_select:
                        gt_status = 1
                    else:
                        gt_status = 2
                else:
                    gt = False
                    gt_status = 0
            except:
                gt = False
                gt_status = 0

    real = float(re.search('Real time \(s\): (.*)', p.stdout)[1])
    cpu = float(re.search('CPU time \(s\): (.*)', p.stdout)[1])
    ram = int(re.search('Max. memory \(cumulated for all children\) \(KiB\): (.*)', p.stdout)[1])

    with open('evaluation/data/' + args.name + '.csv',
              'a') as f:  # TODO use a queue so that only one process needs to have the file open
        writer = csv.writer(f)
        writer.writerow((test_name, timeout, real, cpu, ram, programs, gt, gt_status, status, memout))
        f.flush()


if __name__ == '__main__':
    if not args.append and not args.resume:
        os.mkdir(f'evaluation/data/{args.name}')
        with open('evaluation/data/' + args.name + '.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(('name', 'timeout', 'real', 'cpu', 'ram', 'programs', 'ground_truth', 'gt_status', 'status', 'memout'))
            f.flush()

    textbook = ['tests-examples/textbook/1.yaml', 'tests-examples/textbook/10.yaml', 'tests-examples/textbook/11.yaml', 'tests-examples/textbook/13.yaml', 'tests-examples/textbook/14.yaml', 'tests-examples/textbook/15.yaml', 'tests-examples/textbook/16.yaml', 'tests-examples/textbook/17.yaml', 'tests-examples/textbook/18.yaml', 'tests-examples/textbook/19.yaml', 'tests-examples/textbook/2.yaml', 'tests-examples/textbook/20.yaml', 'tests-examples/textbook/21.yaml', 'tests-examples/textbook/22.yaml', 'tests-examples/textbook/23.yaml', 'tests-examples/textbook/24.yaml', 'tests-examples/textbook/25.yaml', 'tests-examples/textbook/26.yaml', 'tests-examples/textbook/28.yaml', 'tests-examples/textbook/29.yaml', 'tests-examples/textbook/3.yaml', 'tests-examples/textbook/31.yaml', 'tests-examples/textbook/34.yaml', 'tests-examples/textbook/35.yaml', 'tests-examples/textbook/4.yaml', 'tests-examples/textbook/5.yaml', 'tests-examples/textbook/6.yaml', 'tests-examples/textbook/7.yaml', 'tests-examples/textbook/8.yaml', 'tests-examples/textbook/9.yaml']
    scythe_top = ['tests-examples/scythe/top_rated_posts/001.yaml', 'tests-examples/scythe/top_rated_posts/002.yaml', 'tests-examples/scythe/top_rated_posts/003.yaml', 'tests-examples/scythe/top_rated_posts/004.yaml', 'tests-examples/scythe/top_rated_posts/005.yaml', 'tests-examples/scythe/top_rated_posts/006.yaml', 'tests-examples/scythe/top_rated_posts/007.yaml', 'tests-examples/scythe/top_rated_posts/008.yaml', 'tests-examples/scythe/top_rated_posts/009.yaml', 'tests-examples/scythe/top_rated_posts/010.yaml', 'tests-examples/scythe/top_rated_posts/011.yaml', 'tests-examples/scythe/top_rated_posts/012.yaml', 'tests-examples/scythe/top_rated_posts/013.yaml', 'tests-examples/scythe/top_rated_posts/014.yaml', 'tests-examples/scythe/top_rated_posts/016.yaml', 'tests-examples/scythe/top_rated_posts/017.yaml', 'tests-examples/scythe/top_rated_posts/019.yaml', 'tests-examples/scythe/top_rated_posts/021.yaml', 'tests-examples/scythe/top_rated_posts/023.yaml', 'tests-examples/scythe/top_rated_posts/025.yaml', 'tests-examples/scythe/top_rated_posts/027.yaml', 'tests-examples/scythe/top_rated_posts/028.yaml', 'tests-examples/scythe/top_rated_posts/029.yaml', 'tests-examples/scythe/top_rated_posts/031.yaml', 'tests-examples/scythe/top_rated_posts/032.yaml', 'tests-examples/scythe/top_rated_posts/034.yaml', 'tests-examples/scythe/top_rated_posts/036.yaml', 'tests-examples/scythe/top_rated_posts/037.yaml', 'tests-examples/scythe/top_rated_posts/038.yaml', 'tests-examples/scythe/top_rated_posts/043.yaml', 'tests-examples/scythe/top_rated_posts/044.yaml', 'tests-examples/scythe/top_rated_posts/047.yaml', 'tests-examples/scythe/top_rated_posts/048.yaml', 'tests-examples/scythe/top_rated_posts/049.yaml', 'tests-examples/scythe/top_rated_posts/050.yaml', 'tests-examples/scythe/top_rated_posts/051.yaml', 'tests-examples/scythe/top_rated_posts/054.yaml', 'tests-examples/scythe/top_rated_posts/055.yaml', 'tests-examples/scythe/top_rated_posts/057.yaml']
    scythe_recent = ['tests-examples/scythe/recent_posts/003.yaml', 'tests-examples/scythe/recent_posts/004.yaml', 'tests-examples/scythe/recent_posts/007.yaml', 'tests-examples/scythe/recent_posts/009.yaml', 'tests-examples/scythe/recent_posts/011.yaml', 'tests-examples/scythe/recent_posts/012.yaml', 'tests-examples/scythe/recent_posts/013.yaml', 'tests-examples/scythe/recent_posts/016.yaml', 'tests-examples/scythe/recent_posts/019.yaml', 'tests-examples/scythe/recent_posts/021.yaml', 'tests-examples/scythe/recent_posts/028.yaml', 'tests-examples/scythe/recent_posts/031.yaml', 'tests-examples/scythe/recent_posts/032.yaml', 'tests-examples/scythe/recent_posts/034.yaml', 'tests-examples/scythe/recent_posts/036.yaml', 'tests-examples/scythe/recent_posts/038.yaml', 'tests-examples/scythe/recent_posts/040.yaml', 'tests-examples/scythe/recent_posts/042.yaml', 'tests-examples/scythe/recent_posts/044.yaml', 'tests-examples/scythe/recent_posts/045.yaml', 'tests-examples/scythe/recent_posts/046.yaml', 'tests-examples/scythe/recent_posts/051.yaml']
    spider = ['tests-examples/spider/architecture/0003.yaml', 'tests-examples/spider/architecture/0006.yaml', 'tests-examples/spider/architecture/0007.yaml', 'tests-examples/spider/architecture/0008.yaml', 'tests-examples/spider/architecture/0009.yaml', 'tests-examples/spider/architecture/0011.yaml', 'tests-examples/spider/architecture/0012.yaml', 'tests-examples/spider/architecture/0013.yaml', 'tests-examples/spider/architecture/0017.yaml']
    # spider_all_arc = ['tests-examples/spider/architecture/0001.yaml', 'tests-examples/spider/architecture/0002.yaml', 'tests-examples/spider/architecture/0003.yaml', 'tests-examples/spider/architecture/0004.yaml', 'tests-examples/spider/architecture/0005.yaml', 'tests-examples/spider/architecture/0006.yaml', 'tests-examples/spider/architecture/0007.yaml', 'tests-examples/spider/architecture/0008.yaml', 'tests-examples/spider/architecture/0009.yaml', 'tests-examples/spider/architecture/0011.yaml', 'tests-examples/spider/architecture/0012.yaml', 'tests-examples/spider/architecture/0013.yaml', 'tests-examples/spider/architecture/0017.yaml']

    all_instances = textbook + scythe_top + scythe_recent + spider

    if not args.instances:
        instances = all_instances
        # instances = glob.glob('tests-examples/**/**/*.yaml', recursive=True)
        # instances = ['tests-examples/scythe/top_rated_posts/027.yaml']

    else:
        arguments = args.instances.split('+')
        instances = []
        for arg in arguments:
            if 'textbook' in arg:
                instances += textbook
            if 'scythe' in arg:
                flag = True
                if 'top' in arg:
                    instances += scythe_top
                    flag = False
                if 'recent' in arg:
                    instances += scythe_recent
                    flag = False
                if flag:
                    instances += scythe_top + scythe_recent

            if 'spider' in arg:
                instances += spider

        # instances = []
        # with open(args.instances) as inst_list:
        #     for inst in inst_list.readlines():
        #         instances += list(glob.glob(inst[:-1], recursive=True))

    if args.sample:
        instances = random.sample(instances, int(len(instances) * args.sample))

    if args.resume:
        with open('evaluation/data/' + args.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            existing_instances = []
            for row in reader:
                existing_instances.append('tests/' + row[0] + '.yaml')
                print('Skipping', 'tests/' + row[0] + '.yaml')

        instances = filter(lambda x: x not in existing_instances, instances)

    if args.p == 1:
        for i in range(args.n):
            for file in instances:
                test_file(file, f'_{i}')
    else:
        with Pool(processes=args.p) as pool:
            for i in range(args.n):
                pool.map(test_file, instances, chunksize=1)
