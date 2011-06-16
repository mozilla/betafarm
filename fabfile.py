import os

from fabric.api import cd, env, run
from fabric.operations import sudo

env.proj_root = '/var/webapps/betafarm/'
git_repo = 'https://github.com/mozilla/betafarm.git'


def run_manage_cmd(cmd):
    """Run a manage.py command."""
    with cd(env.proj_root):
        run('python manage.py %s' % (cmd,))


def restart_apache():
    sudo('/etc/init.d/apache2 restart')


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
    run_manage_cmd('migrate')


def compress():
    """Compress CSS / Javascript."""
    run_manage_cmd('compress_assets')


def deploy():
    update()
    compress()
    restart_apache()
