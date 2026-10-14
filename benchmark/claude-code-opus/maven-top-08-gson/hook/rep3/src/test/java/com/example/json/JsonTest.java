package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;

import org.junit.jupiter.api.Test;

import tools.jackson.core.JacksonException;

class JsonTest {

    @Test
    void roundTripsRecord() {
        Person original = new Person("Alice", 30, List.of("admin", "dev"));
        String json = Json.write(original);

        assertEquals("{\"name\":\"Alice\",\"age\":30,\"tags\":[\"admin\",\"dev\"]}", json);
        assertEquals(original, Json.parse(json, Person.class));
    }

    @Test
    void readsTree() {
        assertEquals(42, Json.parseTree("{\"user\":{\"id\":42}}").at("/user/id").asInt());
    }

    @Test
    void rejectsMalformedJson() {
        assertThrows(JacksonException.class, () -> Json.parseTree("{not json"));
    }
}
