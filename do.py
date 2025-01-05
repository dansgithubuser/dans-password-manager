#! /usr/bin/env python3

#===== imports =====#
import argparse
import copy
import datetime
import os
import re
import secrets
import string
import subprocess
import sys

#===== args =====#
parser = argparse.ArgumentParser()
parser.add_argument('--docker-build', '--dkrb', action='store_true')
parser.add_argument('--docker-create-env-file', '--dkre', action='store_true')
parser.add_argument('--docker-run', '--dkrr', action='store_true')
parser.add_argument('--docker-db-setup', '--dkrd', action='store_true')
args = parser.parse_args()

#===== consts =====#
DIR = os.path.dirname(os.path.realpath(__file__))

#===== setup =====#
os.chdir(DIR)

#===== helpers =====#
def blue(text):
    return '\x1b[34m' + text + '\x1b[0m'

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())

def invoke(
    *args,
    popen=False,
    no_split=False,
    out=False,
    quiet=False,
    **kwargs,
):
    if len(args) == 1 and not no_split:
        args = args[0].split()
    if not quiet:
        print(blue('-'*40))
        print(timestamp())
        print(os.getcwd()+'$', end=' ')
        if any([re.search(r'\s', i) for i in args]):
            print()
            for i in args: print(f'\t{i} \\')
        else:
            for i, v in enumerate(args):
                if i != len(args)-1:
                    end = ' '
                else:
                    end = ';\n'
                print(v, end=end)
        if kwargs: print(kwargs)
        if popen: print('popen')
        print()
    if kwargs.get('env') != None:
        env = copy.copy(os.environ)
        env.update(kwargs['env'])
        kwargs['env'] = env
    if popen:
        return subprocess.Popen(args, **kwargs)
    else:
        if 'check' not in kwargs: kwargs['check'] = True
        if out: kwargs['capture_output'] = True
        result = subprocess.run(args, **kwargs)
        if out:
            result = result.stdout.decode('utf-8')
            if out != 'exact': result = result.strip()
        return result

def git_state():
    diff = invoke('git diff', out=True)
    diff_cached = invoke('git diff --cached', out=True)
    with open('git-state.txt', 'w') as git_state:
        git_state.write(invoke('git show --name-only', out=True)+'\n')
        if diff:
            git_state.write('\n===== diff =====\n')
            git_state.write(diff+'\n')
        if diff_cached:
            git_state.write('\n===== diff --cached =====\n')
            git_state.write(diff_cached+'\n')

#===== main =====#
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.docker_build:
    git_state()
    invoke('docker build -t dans_password_manager:latest .')

if args.docker_create_env_file:
    secret_key = ''.join(
        secrets.choice(string.ascii_letters + string.digits)
        for i in range(32)
    )
    print('database password:')
    db_pw = input()
    with open('env.txt', 'w') as f:
        f.write(f'DANS_PASSWORD_MANAGER_SECRET_KEY={secret_key}\n')
        f.write(f'DB_DANS_PASSWORD_MANAGER_PASSWORD={db_pw}\n')
        f.write('DB_DANS_PASSWORD_MANAGER_HOST=db\n')

if args.docker_run:
    invoke('docker compose up -d')

if args.docker_db_setup:
    db = 'db_dans_password_manager'
    user = 'u_dans_password_manager'
    with open('env.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('DB_DANS_PASSWORD_MANAGER_PASSWORD'):
            password = line.split('=', 1)[1].strip()
    def psql(command, db=None):
        if db:
            db = f'-d {db}'
        else:
            db = ''
        invoke(*[*f'docker exec -u postgres pwm-db psql {db} -c'.split(), command])
    psql('CREATE DATABASE db_dans_password_manager')
    psql(f"CREATE USER {user} WITH PASSWORD '{password}'")
    psql(f'ALTER ROLE {user} SET client_encoding TO utf8')
    psql(f'ALTER ROLE {user} SET default_transaction_isolation TO "read committed"')
    psql(f'ALTER ROLE {user} SET timezone TO UTC')
    psql(f'GRANT ALL PRIVILEGES ON DATABASE {db} TO {user}')
