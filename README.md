# Satisfactory Mobile

Satisfactory Mobile is a questionnaire optimized for mobile UI.

## Getting Started

1. Clone satisfactory
2. Install pyenv and Python
    * [pyenv] (https://github.com/yyuu/pyenv "pyenv")
    * `pyenv local`
3. Install requirements
    * `pip install -r requirements.txt`
4. Install MySQL Server and create database "satisfactory"
    * MySQL v5.6~
    * `CREATE DATABASE satisfactory DEFAULT CHARACTER SET utf8;`
5. Migrate database and load initial data
    * `python manage.py migrate`
    * `python manage.py loaddata initial_data`
6. Run test
    * `python manage.py test web`
7. Run server and access
    * `python manage.py runserver`

## Deployment

Move dir to `deploy/` for fab commands.

`cd deploy`

### Deploy

Distribute source and start/restart server.

`fab deploy`

### Source distribution

`fab distribute`

### Maintainance on/off

* On
    * `fab maintenance:on`
* Off
    * `fab maintenance:off`

### Start Server

`fab server:start`

### Restart Server

`fab server:restart`

### Stop Server

`fab server:stop`

### Force Quit Server

`fab server:force_quit`

### Migrate

`fab migrate`

### Load data

`fab loaddata:SOME_FIXTURE`

## Set admin password in production

Salt is different from development. You should reset password.

`DJANGO_SETTINGS_MODULE=satisfactory.settings.production python manage.py shell`

```
from web.models import *
user = User.objects.get(pk=1)
user.set_password('new_password')
user.save()
```

This software is released under the MIT License, see LICENSE.txt.
