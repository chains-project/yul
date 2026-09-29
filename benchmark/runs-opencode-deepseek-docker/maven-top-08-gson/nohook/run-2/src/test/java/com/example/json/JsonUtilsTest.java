package com.example.json;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JsonUtilsTest {

    @Test
    void serializesUserToJson() {
        User user = new User(1L, "Grace Hopper", "grace@example.com",
                List.of("admin"), Instant.parse("2026-02-01T12:00:00Z"));

        String json = JsonUtils.toJson(user);

        assertTrue(json.contains("\"name\" : \"Grace Hopper\""));
        assertTrue(json.contains("\"createdAt\" : \"2026-02-01T12:00:00Z\""));
    }

    @Test
    void parsesUserFromJson() {
        String json = """
                {
                  "id" : 7,
                  "name" : "Alan Turing",
                  "email" : "alan@example.com",
                  "roles" : [ "developer" ],
                  "createdAt" : "2026-03-10T08:15:00Z"
                }
                """;

        User user = JsonUtils.fromJson(json, User.class);

        assertEquals(7L, user.getId());
        assertEquals("Alan Turing", user.getName());
        assertEquals(List.of("developer"), user.getRoles());
        assertEquals(Instant.parse("2026-03-10T08:15:00Z"), user.getCreatedAt());
    }

    @Test
    void roundTripsUser() {
        User user = new User(99L, "Katherine Johnson", "katherine@example.com",
                List.of("analyst", "admin"), Instant.parse("2026-04-05T17:45:00Z"));

        User parsed = JsonUtils.fromJson(JsonUtils.toJson(user), User.class);

        assertEquals(user, parsed);
    }

    @Test
    void parsesJsonArray() {
        String json = """
                [
                  { "id" : 1, "name" : "A", "email" : "a@example.com", "roles" : [], "createdAt" : "2026-01-01T00:00:00Z" },
                  { "id" : 2, "name" : "B", "email" : "b@example.com", "roles" : [ "user" ], "createdAt" : "2026-01-02T00:00:00Z" }
                ]
                """;

        List<User> users = JsonUtils.fromJsonList(json, User.class);

        assertEquals(2, users.size());
        assertEquals("B", users.get(1).getName());
    }
}
