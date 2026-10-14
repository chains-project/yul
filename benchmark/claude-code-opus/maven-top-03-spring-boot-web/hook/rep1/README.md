# api

Spring Boot 4.1 REST API (Java 25, Maven).

## Run

```bash
./mvnw spring-boot:run        # starts on http://localhost:8080
./mvnw verify                 # build + tests
java -jar target/api-0.0.1-SNAPSHOT.jar
```

## Endpoints

| Method | Path              | Description        |
|--------|-------------------|--------------------|
| GET    | /api/items        | List items         |
| GET    | /api/items/{id}   | Get one item       |
| POST   | /api/items        | Create (201 + Location) |
| PUT    | /api/items/{id}   | Replace            |
| DELETE | /api/items/{id}   | Delete (204)       |
| GET    | /actuator/health  | Health check       |

Errors are returned as RFC 9457 `application/problem+json`.
