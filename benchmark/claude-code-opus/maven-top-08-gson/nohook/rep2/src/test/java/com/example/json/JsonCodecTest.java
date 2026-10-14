package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;

import org.junit.jupiter.api.Test;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;

class JsonCodecTest {

    @Test
    void roundTripsRecord() {
        Person person = new Person("Ada", 36, List.of("ada@example.com"));

        String json = JsonCodec.toJson(person);

        assertEquals("{\"name\":\"Ada\",\"age\":36,\"emails\":[\"ada@example.com\"]}", json);
        assertEquals(person, JsonCodec.fromJson(json, Person.class));
    }

    @Test
    void parsesTree() {
        JsonNode node = JsonCodec.parseTree("{\"a\":{\"b\":[1,2,3]}}");

        assertEquals(3, node.at("/a/b/2").asInt());
    }

    @Test
    void rejectsMalformedJson() {
        assertThrows(JacksonException.class, () -> JsonCodec.parseTree("{not json"));
    }
}
