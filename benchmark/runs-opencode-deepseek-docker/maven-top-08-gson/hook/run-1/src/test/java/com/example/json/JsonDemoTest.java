package com.example.json;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JsonDemoTest {

    private final JsonDemo demo = new JsonDemo();

    @Test
    void generatesJsonFromObject() throws Exception {
        String json = demo.toJson(new JsonDemo.Person("Ada", 36, List.of("math", "computing")));

        assertTrue(json.contains("\"name\":\"Ada\""));
        assertTrue(json.contains("\"age\":36"));
    }

    @Test
    void parsesJsonIntoObject() throws Exception {
        JsonDemo.Person person = demo.fromJson(
                "{\"name\":\"Grace\",\"age\":45,\"hobbies\":[\"compilers\"]}");

        assertEquals("Grace", person.name());
        assertEquals(45, person.age());
        assertEquals(List.of("compilers"), person.hobbies());
    }

    @Test
    void parsesJsonTree() throws Exception {
        JsonNode node = demo.readTree("{\"a\":{\"b\":[1,2,3]}}");

        assertEquals(2, node.path("a").path("b").path(1).asInt());
    }
}
