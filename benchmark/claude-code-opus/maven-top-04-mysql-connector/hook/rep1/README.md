# mysql-jdbc-app

Minimal Maven project that connects to MySQL with plain JDBC (MySQL Connector/J).

## Requirements

- JDK 21+
- Maven 3.9+
- A MySQL server (or Docker, see below)

## Start a local MySQL

```sh
docker compose up -d   # creates database `appdb`, user `app`/`app`, and loads db/schema.sql
```

## Configure

Connection settings come from environment variables:

| Variable      | Default                              |
|---------------|--------------------------------------|
| `DB_URL`      | `jdbc:mysql://localhost:3306/appdb`  |
| `DB_USER`     | *(required)*                         |
| `DB_PASSWORD` | empty                                |

## Build, test, run

```sh
mvn verify
DB_USER=app DB_PASSWORD=app mvn -q compile exec:java
```

## Layout

- `com.example.db.DatabaseConfig` – reads connection settings from the environment
- `com.example.db.Database` – opens connections via `DriverManager`
- `com.example.db.UserRepository` – example queries using `PreparedStatement` and try-with-resources
- `com.example.App` – entry point: prints the server version and lists users
