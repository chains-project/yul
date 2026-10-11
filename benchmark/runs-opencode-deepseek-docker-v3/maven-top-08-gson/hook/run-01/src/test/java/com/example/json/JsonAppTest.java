package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class JsonAppTest {

    private final JsonApp app = new JsonApp();

    @Test
    void generatesJson() throws Exception {
        String json = app.toJson(new User(1L, "Ada Lovelace", "ada@example.com"));

        assertTrue(json.contains("\"id\" : 1"));
        assertTrue(json.contains("\"name\" : \"Ada Lovelace\""));
        assertTrue(json.contains("\"email\" : \"ada@example.com\""));
    }

    @Test
    void parsesJson() throws Exception {
        String json = "{\"id\":2,\"name\":\"Alan Turing\",\"email\":\"alan@example.com\"}";

        User user = app.fromJson(json);

        assertEquals(new User(2L, "Alan Turing", "alan@example.com"), user);
    }

    @Test
    void roundTrips() throws Exception {
        User original = new User(3L, "Grace Hopper", "grace@example.com");

        assertEquals(original, app.fromJson(app.toJson(original)));
    }
}
