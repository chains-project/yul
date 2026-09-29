package com.example.jsonapp;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class JsonAppTest {

    private final JsonApp app = new JsonApp();

    @Test
    void generatesJson() throws JsonProcessingException {
        Person person = new Person("Ada Lovelace", 36, List.of("mathematics", "programming"));

        String json = app.toJson(person);

        assertEquals(
                "{\"name\":\"Ada Lovelace\",\"age\":36,\"hobbies\":[\"mathematics\",\"programming\"]}",
                json);
    }

    @Test
    void parsesJson() throws JsonProcessingException {
        String json = "{\"name\":\"Grace Hopper\",\"age\":85,\"hobbies\":[\"compilers\"]}";

        Person person = app.fromJson(json);

        assertEquals(new Person("Grace Hopper", 85, List.of("compilers")), person);
    }

    @Test
    void roundTrips() throws JsonProcessingException {
        Person original = new Person("Alan Turing", 41, List.of("cryptography"));

        assertEquals(original, app.fromJson(app.toJson(original)));
    }
}
