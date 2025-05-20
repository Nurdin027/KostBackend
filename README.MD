# Kost Backend

<details>
<summary>
Database configuration & migration
</summary> 

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

</details>


