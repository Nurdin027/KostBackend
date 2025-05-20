# Kost Backend

## Config virtual environment and install packages

### create virtualenv

```shell
virtuealenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Database configuration & migration

### create .env

```shell
cp .example.env .env
```

### create database kost_db

```sql
create database kost_db;
```

### migrate database

```shell
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Running Project

```shell
flask run
```

## URL:

- debug: http://localhost:5000/
- documentation: http://localhost:5000/swagger/

Create admin at /api/auth/create-admin for login
