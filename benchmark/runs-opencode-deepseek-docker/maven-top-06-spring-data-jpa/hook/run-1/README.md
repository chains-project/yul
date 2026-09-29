# inventory-service

Spring Boot service that persists data to a relational database through
Spring Data JPA / Hibernate repositories.

## Stack

| Component      | Version |
| -------------- | ------- |
| Java           | 21      |
| Spring Boot    | 4.1.1   |
| Spring Data JPA / Hibernate | managed by Boot |
| Build          | Maven   |
| Database (dev) | H2 (in-memory) |
| Database (prod example) | PostgreSQL |

## Layout

```
src/main/java/com/example/inventory
├── InventoryApplication.java          # @SpringBootApplication entry point
├── domain/Product.java                # @Entity with @Version optimistic locking
├── repository/ProductRepository.java  # JpaRepository + derived queries
├── service/ProductService.java        # @Transactional business logic
└── web/                               # REST controller, DTOs, error handling
```

## Run

The default profile uses an in-memory H2 database, so no setup is required:

```bash
mvn spring-boot:run
```

H2 console: <http://localhost:8080/h2-console> (JDBC URL `jdbc:h2:mem:inventory`, user `sa`, empty password).

### PostgreSQL

Start the bundled database and run with the `postgres` profile:

```bash
docker compose up -d
mvn spring-boot:run -Dspring-boot.run.profiles=postgres
```

Connection settings are read from environment variables (with sensible defaults):

| Variable                 | Default                                      |
| ------------------------ | -------------------------------------------- |
| `JDBC_DATABASE_URL`      | `jdbc:postgresql://localhost:5432/inventory` |
| `JDBC_DATABASE_USERNAME` | `inventory`                                  |
| `JDBC_DATABASE_PASSWORD` | `inventory`                                  |
| `DB_POOL_SIZE`           | `10`                                         |

## REST API

| Method | Path                      | Description                    |
| ------ | ------------------------- | ------------------------------ |
| GET    | `/api/products`           | List products (`?name=` filter)|
| GET    | `/api/products/{id}`      | Fetch one product              |
| GET    | `/api/products/by-sku/{sku}` | Fetch by SKU                |
| POST   | `/api/products`           | Create a product               |
| PUT    | `/api/products/{id}`      | Update a product               |
| DELETE | `/api/products/{id}`      | Delete a product               |

```bash
curl -X POST http://localhost:8080/api/products \
  -H 'Content-Type: application/json' \
  -d '{"sku":"SKU-1","name":"Widget","price":9.99,"quantity":5}'
```

Validation errors and missing resources are returned as RFC 7807 `ProblemDetail` responses.

## Test

```bash
mvn test
```

Tests use H2 via `@DataJpaTest` (repository) and `@SpringBootTest` + MockMvc (web layer).

## Production notes

The PostgreSQL profile currently uses `spring.jpa.hibernate.ddl-auto=update` for
convenience. For production, add Flyway or Liquibase and switch `ddl-auto` to
`validate` so schema changes are versioned and reviewed.
