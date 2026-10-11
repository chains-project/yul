package com.example.json;

import com.fasterxml.jackson.core.type.TypeReference;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JsonDemoTest {

    @Test
    void roundTripsTypedObject() {
        User user = new User(
                7L,
                "Alan Turing",
                "alan@example.com",
                true,
                Instant.parse("2026-02-01T08:00:00Z"),
                List.of("researcher"));

        User parsed = JsonDemo.fromJson(JsonDemo.toJson(user), User.class);

        assertEquals(user, parsed);
    }

    @Test
    void parsesIntoGenericMap() {
        Map<String, Object> parsed = JsonDemo.fromJson(
                "{\"name\":\"Grace\",\"active\":true}",
                new TypeReference<>() {
                });

        assertEquals("Grace", parsed.get("name"));
        assertEquals(true, parsed.get("active"));
    }

    @Test
    void ignoresUnknownProperties() {
        User parsed = JsonDemo.fromJson(
                "{\"id\":1,\"name\":\"n\",\"email\":\"e\",\"active\":false,"
                        + "\"createdAt\":\"2026-01-01T00:00:00Z\",\"roles\":[],\"extra\":123}",
                User.class);

        assertEquals(1L, parsed.id());
        assertTrue(parsed.roles().isEmpty());
    }
}
