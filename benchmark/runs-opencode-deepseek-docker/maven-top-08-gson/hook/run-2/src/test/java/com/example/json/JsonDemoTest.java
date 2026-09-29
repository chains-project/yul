package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class JsonDemoTest {

    @Test
    void generatesAndParsesRoundTrip() throws Exception {
        Person person = new Person("Ada Lovelace", 36, "ada@example.com");

        String json = JsonDemo.toJson(person);
        Person parsed = JsonDemo.fromJson(json, Person.class);

        assertEquals(person.getName(), parsed.getName());
        assertEquals(person.getAge(), parsed.getAge());
        assertEquals(person.getEmail(), parsed.getEmail());
    }

    @Test
    void parsesTree() throws Exception {
        var tree = JsonDemo.parseTree("{\"name\":\"Grace\",\"age\":45}");

        assertEquals("Grace", tree.get("name").asText());
        assertEquals(45, tree.get("age").asInt());
    }

    @Test
    void addsExtraField() throws Exception {
        String json = JsonDemo.toJsonWithExtraField(new Person("Alan", 41, "alan@example.com"), "role", "admin");

        assertEquals("admin", JsonDemo.parseTree(json).get("role").asText());
    }
}
