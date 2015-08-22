from fabric.api import *
from fabric.colors import cyan, red, green, yellow
from fabric.operations import put
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

# Configure these
env.hosts = ['']
env.user = ''
env.key_filename = ''

def deploy():
    print(cyan('Deploying...'))
    distribute()
    if (exists('/tmp/satisfactory.pid') and exists('/proc/`cat /tmp/satisfactory.pid`')):
        server('restart')
    else:
        server('start')
    print(green('Deployment done!'))

def distribute():
    print(cyan('Distributing...'))
    rsync_project(
            local_dir='../../satisfactory/',
            remote_dir='/home/satisfactory/deploy/satisfactory',
            exclude=['.DS_Store', '*.tmp', '.git', '*.log'],
            delete=True,
            )
    with cd('/home/satisfactory/deploy/satisfactory'):
        run("pip install -r requirements.txt")
    sudo("rsync -pthrvz /home/satisfactory/deploy/satisfactory/web/static /usr/share/nginx/satisfactory/")
    print(green('Distribution done!'))

def maintenance(switch):
    if (switch == 'on'):
        if (exists('/usr/share/nginx/in_maintenance', use_sudo=True)):
            abort(red('Already in maintenance.'))
        else:
            print(cyan('Switching maintenance on...'))
            sudo("touch /usr/share/nginx/in_maintenance")
            print(green('Switched maintenance on!'))
    elif (switch == 'off'):
        if (exists('/usr/share/nginx/in_maintenance', use_sudo=True)):
            print(cyan('Switching maintenance off...'))
            sudo("rm /usr/share/nginx/in_maintenance")
            print(green('Switched maintenance off!'))
        else:
            abort(red('Already out of maintenance.'))
    else:
        abort(yellow('Give `on` or `off` as param.'))

def server(operation):
    if (operation == 'start'):
        print(cyan('Starting server...'))
        with cd('/home/satisfactory/deploy/satisfactory'):
            run("gunicorn -w 4 --daemon --pid /tmp/satisfactory.pid --env DJANGO_SETTINGS_MODULE=satisfactory.settings.production satisfactory.wsgi")
        print(green('Server started!'))
    elif (operation == 'restart'):
        print(cyan('Restarting server...'))
        with cd('/home/satisfactory/deploy/satisfactory'):
            run("kill -HUP `cat /tmp/satisfactory.pid`")
        print(green('Server restarted!'))
    elif (operation == 'stop'):
        print(cyan('Stoping server...'))
        with cd('/home/satisfactory/deploy/satisfactory'):
            run("kill -TERM `cat /tmp/satisfactory.pid`")
        print(green('Server stopped!'))
    elif (operation == 'force_quit'):
        print(cyan('Force quitting server...'))
        with cd('/home/satisfactory/deploy/satisfactory'):
            run("kill -QUIT `cat /tmp/satisfactory.pid`")
        print(green('Server force quit!'))
    else:
        abort(yellow('Give `start|restart|stop|force_quit` as param.'))

def migrate():
    print(cyan('Migrating...'))
    with cd('/home/satisfactory/deploy/satisfactory'):
        run("DJANGO_SETTINGS_MODULE=satisfactory.settings.production python manage.py migrate")
    print(green('Migration done!'))

def loaddata(fixture):
    print(cyan('Loading data...'))
    with cd('/home/satisfactory/deploy/satisfactory'):
        run("DJANGO_SETTINGS_MODULE=satisfactory.settings.production python manage.py loaddata {0}".format(fixture))
    print(green('Data loaded!'))
