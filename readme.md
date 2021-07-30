# eRegister

Digital version of school register.

### Live demo

Soon

## Installation

To install required packages, `cd` to project's root directory and run command:

```
pip install -r requirements.txt
```

#### Development server

Firstly, create `eregister/settings_local.py` or rename existing `settings_local.example.py`. New file should contain `SECRET_KEY` and `DATABASES` variables. (See _Settings_ section)

Migrate database by running:

```
python manage.py migrate
```

To start local server, run command:

```
python manage.py runserver
```

## Settings

#### Local settings

By default `SECRET_KEY` and `DATABASES` settings are imported from `eregister/settings_local.py`. The file should look like this:

```python
SECRET_KEY = 'your_secret_key'

DATABASES = {
    'default': (...)
}

```

To use local _SQLite_ database, `DATABASES` can be set to:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Default permissions groups

By default three Groups are created: _Students_, _Teachers_ and _Educators_. Default permissions are set in `eregister/settings.py`:

```python
DEFAULT_GROUPS = {
    'Students': [
        (...)
    ],
    'Teachers': [
        (...)
    ],
    'Educators': [
        (...)
    ]
}
```

Groups are created post every migration. Note that default permissions are assigned **only to newly created group**. If you modify `DEFAULT_GROUPS` setting, groups already existing in database won't be modified.

To alter these groups, you can use Django's admin panel or you can run command:

```
python manage.py syncgroups
```

This will create missing groups and alter existing ones' permissions to specified in `DEFAULT_GROUPS` setting.
