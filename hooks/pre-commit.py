"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/python
import subprocess


def normalize_output(lines):
    filtered = filter(lambda x: x and len(x) > 0, lines)
    return list(map(lambda x: x.rstrip(), filtered))


def run_cmd(args):
    process = subprocess.run(args, stdout=subprocess.PIPE)
    return process.returncode, normalize_output(process.stdout.decode('utf-8').split('\n'))


def check_requirements():
    freeze = run_cmd(['pip', 'freeze'])[1]
    lines = normalize_output(open('requirements.txt', 'r').readlines())
    return 0 if freeze == lines else 1, []


def run_flake():
    return run_cmd(['flake8'])


def run_step(title, func):
    print(f'\nRunning: {title} ... ')
    try:
        result = func()
        if len(result[1]) > 0:
            print('\n'.join(result[1]))
        return result[0]
    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    print('Running pre commit hook\n\n')
    steps = [
        ('Flake8', run_flake),
        ('Requirements.txt check', check_requirements)
    ]
    results = []

    failed_count = 0
    for curr_step in steps:
        curr_result = run_step(curr_step[0], curr_step[1])
        results.append((curr_step[0], curr_result))
        if curr_result != 0:
            failed_count += 1

    print('\n\n')

    for curr_result in results:
        status_msg = 'OK' if curr_result[1] == 0 else 'FAIL'
        print(f'{curr_result[0]} {status_msg}')

    status_msg = 'successfully' if failed_count == 0 else f'with {failed_count} failures'
    print(f'\nPre commit hook finished {status_msg}')
    exit(1 if failed_count > 0 else 0)
