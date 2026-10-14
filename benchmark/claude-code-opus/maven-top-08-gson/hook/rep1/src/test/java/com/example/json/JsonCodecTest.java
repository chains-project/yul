package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import org.junit.jupiter.api.Test;
import tools.jackson.databind.JsonNode;

class JsonCodecTest {

    @Test
    void roundTripsRecord() {
        Person original = new Person("Ada", 36, List.of("math"));
        String json = JsonCodec.toJson(original);
        assertEquals(original, JsonCodec.parse(json, Person.class));
    }

    @Test
    void parsesTree() {
        JsonNode node = JsonCodec.parseTree("{\"name\":\"Ada\",\"tags\":[\"a\",\"b\"]}");
        assertEquals("Ada", node.get("name").asString());
        assertEquals(2, node.get("tags").size());
    }
}
