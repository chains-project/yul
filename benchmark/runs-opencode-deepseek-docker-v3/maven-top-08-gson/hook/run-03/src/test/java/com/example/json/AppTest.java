package com.example.json;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AppTest {

    private final App app = new App();

    @Test
    void roundTripsPerson() throws Exception {
        Person original = new Person("Ada Lovelace", 36, List.of("mathematics", "programming"));

        String json = app.toJson(original);
        Person parsed = app.fromJson(json);

        assertEquals(original, parsed);
    }

    @Test
    void generatesExpectedJson() throws Exception {
        Person person = new Person("Ada Lovelace", 36, List.of("mathematics"));

        String json = app.toJson(person);

        assertTrue(json.contains("\"name\":\"Ada Lovelace\""));
        assertTrue(json.contains("\"age\":36"));
    }

    @Test
    void prettyPrintsJson() throws Exception {
        String pretty = app.prettyJson("{\"name\":\"Ada\",\"age\":36}");

        assertTrue(pretty.contains("\n"));
        assertTrue(pretty.contains("\"name\" : \"Ada\""));
    }
}
