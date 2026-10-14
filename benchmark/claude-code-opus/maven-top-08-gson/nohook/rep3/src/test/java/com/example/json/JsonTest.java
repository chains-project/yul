package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;

import org.junit.jupiter.api.Test;

import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;

class JsonTest {

    @Test
    void roundTripsRecord() {
        Person original = new Person("Alice", 30, List.of("admin", "dev"));

        String json = Json.toJson(original);

        assertEquals("{\"name\":\"Alice\",\"age\":30,\"tags\":[\"admin\",\"dev\"]}", json);
        assertEquals(original, Json.fromJson(json, Person.class));
    }

    @Test
    void parsesTree() {
        JsonNode node = Json.parseTree("{\"a\":{\"b\":[1,2,3]}}");

        assertEquals(3, node.at("/a/b").size());
        assertEquals(2, node.at("/a/b/1").asInt());
    }

    @Test
    void rejectsMalformedJson() {
        assertThrows(JacksonException.class, () -> Json.parseTree("{not json"));
    }
}
