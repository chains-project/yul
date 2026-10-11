package com.example.jsonapp;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class JsonServiceTest {

    private final JsonService json = new JsonService();

    @Test
    void generatesJson() throws Exception {
        String encoded = json.toJson(new User(1L, "Ada Lovelace", "ada@example.com"));

        assertTrue(encoded.contains("\"id\" : 1"));
        assertTrue(encoded.contains("\"name\" : \"Ada Lovelace\""));
        assertTrue(encoded.contains("\"email\" : \"ada@example.com\""));
    }

    @Test
    void parsesJson() throws Exception {
        String input = "{\"id\":7,\"name\":\"Alan Turing\",\"email\":\"alan@example.com\"}";

        User user = json.fromJson(input, User.class);

        assertEquals(new User(7L, "Alan Turing", "alan@example.com"), user);
    }

    @Test
    void roundTrips() throws Exception {
        User original = new User(42L, "Grace Hopper", "grace@example.com");

        User restored = json.fromJson(json.toJson(original), User.class);

        assertEquals(original, restored);
    }
}
