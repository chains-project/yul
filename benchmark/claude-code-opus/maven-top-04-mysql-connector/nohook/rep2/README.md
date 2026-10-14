# mysql-jdbc-app

A small Maven project that connects to MySQL with JDBC (MySQL Connector/J).

## Requirements
- JDK 21 or newer
- Maven 3.9 or newer
- A MySQL server you can reach

## Configuration
Defaults are in `src/main/resources/db.properties`. You can override each one. Values are checked in this order:

| Setting  | System property | Env var       |
|----------|-----------------|---------------|
| URL      | `db.url`        | `DB_URL`      |
| User     | `db.user`       | `DB_USER`     |
| Password | `db.password`   | `DB_PASSWORD` |

Keep real credentials out of `db.properties`. Use env vars instead.

## Run
```bash
mvn test                                   # unit tests (no DB needed)
DB_URL='jdbc:mysql://localhost:3306/mydb' DB_USER=app DB_PASSWORD=secret mvn compile exec:java
```

For a local MySQL in Docker:
```bash
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=mydb -p 3306:3306 mysql:8
```

## Usage
```java
Database db = new Database(DatabaseConfig.load());
List<String> names = db.query("SELECT name FROM users WHERE age > ?", rs -> rs.getString("name"), 18);
int updated = db.update("UPDATE users SET active = ? WHERE id = ?", true, 42);
```
Pass values as `?` parameters. Don't concatenate them into the SQL.
