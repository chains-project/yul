package com.example.jsondemo;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;

import org.junit.jupiter.api.Test;

import com.example.jsondemo.model.Person;
import com.fasterxml.jackson.databind.JsonNode;

class JsonServiceTest {

    private final JsonService service = new JsonService();

    @Test
    void parsesPersonFromJson() throws Exception {
        String json = """
                {"name":"Ada Lovelace","age":36,"email":"ada@example.com",
                 "roles":["admin","engineer"]}
                """;

        Person person = service.parsePerson(json);

        assertEquals("Ada Lovelace", person.name());
        assertEquals(36, person.age());
        assertEquals(List.of("admin", "engineer"), person.roles());
    }

    @Test
    void parsesNestedTree() throws Exception {
        JsonNode tree = service.parseTree("{\"user\":{\"id\":7,\"active\":true}}");

        assertEquals(7, tree.path("user").path("id").asInt());
        assertTrue(tree.path("user").path("active").asBoolean());
    }

    @Test
    void generatesJsonRoundTrip() throws Exception {
        Person original = new Person("Grace Hopper", 85, "grace@example.com", List.of("author"));
        String json = service.toJson(original);

        assertEquals(original, service.parsePerson(json));
    }
}
