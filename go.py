import os
import sys

DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(DIR, 'deps'))

import djangogo

parser = djangogo.make_parser()
args = parser.parse_args()
djangogo.main(args,
    project='proj_dans_password_manager',
    app='dans_password_manager',
    db_name='db_dans_password_manager',
    db_user='u_dans_password_manager',
    heroku_url='https://dans-password-manager.herokuapp.com/',
    heroku_repo='https://git.heroku.com/dans-password-manager.git',
)
