# mysql-jdbc-demo

Maven Java project that connects to and queries a MySQL database over JDBC.

## Requirements

- JDK 21+
- Maven 3.9+
- A reachable MySQL server

## Configuration

Connection settings live in `src/main/resources/db.properties`:

```
db.url=jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC
db.user=root
db.password=change-me
```

They can be overridden with environment variables (useful for CI/containers):
`DB_URL`, `DB_USER`, `DB_PASSWORD`.

## Build and run

```bash
mvn clean package
java -jar target/mysql-jdbc-demo.jar
```

Or run directly from source:

```bash
mvn compile exec:java
```

## Query used

`Main` runs the prepared statement:

```sql
SELECT id, name FROM users WHERE name LIKE ? ORDER BY id
```

Adjust the SQL and the `users` table to match your schema.
