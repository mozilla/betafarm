import os

from fabric.api import cd, env, run

env.proj_root = '/var/webapps/betafarm/'
git_repo = 'https://github.com/mozilla/betafarm.git'


def clone():
    """Create project directory and clone repository."""
    with cd(os.path.dirname(env.proj_root.rstrip('/'))):
        run('git clone --recursive %s' % (git_repo,))


def update():
    """Update project source."""
    with cd(env.proj_root):
        run('git pull origin master')


def migrate():
    """Run database migrations."""
    with cd(env.proj_root):
        run('python manage.py migrate')


def deploy():
    update()
