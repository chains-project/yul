# api

Spring Boot 4.1 REST API (Java 25, Maven).

## Build & run

```bash
./mvnw verify            # compile + run tests
./mvnw spring-boot:run   # start on http://localhost:8080
```

## Endpoints

| Method | Path              | Description        |
|--------|-------------------|--------------------|
| GET    | /api/items        | List items         |
| GET    | /api/items/{id}   | Get an item        |
| POST   | /api/items        | Create an item     |
| PUT    | /api/items/{id}   | Replace an item    |
| DELETE | /api/items/{id}   | Delete an item     |
| GET    | /actuator/health  | Health check       |

Errors are returned as RFC 9457 `application/problem+json`.
