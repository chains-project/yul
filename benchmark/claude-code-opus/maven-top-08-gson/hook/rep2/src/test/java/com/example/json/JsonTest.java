package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;

class JsonTest {

    @Test
    void roundTripsRecord() {
        Person original = new Person("Bob", 42, List.of("a", "b"));
        assertEquals(original, Json.parse(Json.write(original), Person.class));
    }

    @Test
    void generatesExpectedJson() {
        Person p = new Person("Bob", 42, List.of("x"));
        assertEquals("{\"name\":\"Bob\",\"age\":42,\"tags\":[\"x\"]}", Json.write(p));
    }

    @Test
    void parsesTree() {
        JsonNode node = Json.parseTree("{\"items\":[1,2,3],\"ok\":true}");
        assertEquals(3, node.get("items").size());
        assertTrue(node.get("ok").asBoolean());
    }

    @Test
    void rejectsMalformedJson() {
        assertThrows(JacksonException.class, () -> Json.parseTree("{not json"));
    }
}
