# Monitora - demo

## Task [CSFD ukol](./CSFD ukol.pdf)


## 1. Instalation
This project use poetry virtual enviroments. Poetry documentation: https://python-poetry.org/docs/

For simple use for development, use [Makefile](./Makefile) commands:

### First install
Install and upgrade based package like poetry, setuptools, wheel, pip, virtualenv.
Install too pre-commit package, when is uses for check code quality.

```
make install
```

For production enviroment use:
```
make install-deploy
```

#### Uninstall & Reinstall
```
make uninstall

or

make reinstall
```

## 2. Settings Enviroments
Is possible for development use .env file in root directory, when is automaticly loaded on start.

Enviroment variables:
* SWAGGER_UI=true | false
* DEBUG=true | false
* SECRET_KEY=<DJANGO_SECRET_KEY - hash>

Database settings:
* `DATABASE_DRIVER=` - support postgresql | sqlite, default is sqlite
* `DATABASE_NAME=`
* `DATABASE_USER=`
* `DATABASE_HOST=`
* `DATABASE_PORT=`
* `DATABASE_PASSWORD=`



## 3. Migrate database
For next step, needed create database and dump movies.

```
make migrate
```

Create new migration, use command:
```
make migration-generate
```

Clear database
```
make database-recreate
```

### Add supervisor or another users
```
poetry run python3 manage.py createsuperuser --username=admin --email=admin@monitora.cz

poetry run python3 manage.py createuser --username=staff --email=staff@monitora.cz
```
### Dump first data - Actors & Movies
Optional CI arguments:

* --count  default=300)
* --clear-database
* --set-default-password
* --full-actors


```
make dump-movies

# or if need load all actors, use this command

make dump-movies-full
```

## 6. Start server
```
make start
```
Open browser and enter http://127.0.0.1, automatic redirect to http://127.0.0.1/index.
Need logged as admin or staff.




## 7. Testing
#### Functional tests
```
make test
```
#### Performance test
```
make perf-test
```

### 8. Code pretty & sort imports & lint
```
make pretty

make isort

make lint
```

## Docker

### Build
```
make docker-build
```
or with cache
```
make docker-build-cache
```
### Run
```
make docker-run
```

## Docker-compose

### Install
```
make docker-compose-install
```
### Build
```
make docker-compose-build
```
or with cache
```
make docker-compose-build-cache
```
### start
```
make docker-compose-up
```

## Changelog
- 1.0.0: Create project.
- 1.1.0: Update api MovirSerializer. Added tests.
