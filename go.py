import os
import shutil
import sys

DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(DIR, 'deps'))

import djangogo

parser = djangogo.make_parser()
parser.add_argument('--frontend-build', '--fb', action='store_true')
args = parser.parse_args()

if args.frontend_build:
    os.chdir('frontend')
    djangogo.invoke('npm', 'run', 'build')
    os.chdir('..')
    dst = os.path.join('dans_password_manager', 'static', 'dans_password_manager')
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join('frontend', 'dist'), dst)
else: djangogo.main(args,
    project='proj_dans_password_manager',
    app='dans_password_manager',
    db_name='db_dans_password_manager',
    db_user='u_dans_password_manager',
    heroku_url='https://dans-password-manager.herokuapp.com/',
    heroku_repo='https://git.heroku.com/dans-password-manager.git',
)
