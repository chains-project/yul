# mysql-jdbc-app

Minimal Maven project that connects to MySQL via JDBC (MySQL Connector/J).

## Requirements
- JDK 21+
- Maven 3.9+
- A reachable MySQL server

## Configuration
Settings resolve in this order: JVM system property → environment variable → `src/main/resources/db.properties`.

| Property      | Env var       | Default                                         |
|---------------|---------------|-------------------------------------------------|
| `db.url`      | `DB_URL`      | `jdbc:mysql://localhost:3306/mydb?serverTimezone=UTC` |
| `db.user`     | `DB_USER`     | `root`                                          |
| `db.password` | `DB_PASSWORD` | *(empty)*                                       |

Don't commit real passwords to `db.properties`; use `DB_PASSWORD` instead.

## Build & run
```sh
mvn package                                   # compile + run tests
DB_PASSWORD=secret mvn -q exec:java           # connects, prints server version, runs SHOW TABLES
mvn -q exec:java -Dexec.args="SELECT * FROM users LIMIT 5"
```

## Using it in code
```java
Database db = new Database(DbConfig.load());
List<Map<String, Object>> rows = db.query("SELECT id, name FROM users WHERE id = ?", 42);
int updated = db.update("UPDATE users SET name = ? WHERE id = ?", "Ada", 42);
```
Always pass values as `?` parameters, not by building SQL strings yourself, so you're protected against SQL injection.

## Quick local MySQL
```sh
docker run -d --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=mydb mysql:8
```
