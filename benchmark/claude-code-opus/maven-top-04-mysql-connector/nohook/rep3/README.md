# mysql-jdbc-app

Minimal Maven project that connects to MySQL via JDBC (`com.mysql:mysql-connector-j`).

## Requirements
- JDK 21+
- Maven 3.9+
- A reachable MySQL server

## Configuration
Set via environment variables:

| Variable      | Default                              |
|---------------|--------------------------------------|
| `DB_URL`      | `jdbc:mysql://localhost:3306/test`   |
| `DB_USER`     | `root`                               |
| `DB_PASSWORD` | *(empty)*                            |

## Build & run
```sh
mvn test                      # unit tests (no database needed)
DB_URL=jdbc:mysql://localhost:3306/mydb DB_USER=me DB_PASSWORD=secret \
  mvn -q compile exec:java    # prints server version and lists tables
```

Quick local MySQL for testing:
```sh
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=test -p 3306:3306 mysql:8
```

## Usage
```java
Database db = new Database(DatabaseConfig.fromEnvironment());
List<String> names = db.query(
        "SELECT name FROM users WHERE active = ?", rs -> rs.getString("name"), true);
int rows = db.update("UPDATE users SET active = ? WHERE id = ?", false, 42);
```
Always pass values as `?` parameters (never string concatenation) to avoid SQL injection.
