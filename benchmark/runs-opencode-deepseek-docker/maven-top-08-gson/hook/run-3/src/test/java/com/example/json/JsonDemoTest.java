package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;

class JsonDemoTest {

    private final JsonDemo demo = new JsonDemo();

    @Test
    void generatesAndParsesRoundTrip() throws Exception {
        Person original = new Person("Ada Lovelace", 36, "ada@example.com", List.of("math", "code"));

        String json = demo.toJson(original);

        assertTrue(json.contains("\"name\" : \"Ada Lovelace\""));
        assertEquals(original, demo.fromJson(json));
    }

    @Test
    void parsesJsonIgnoringUnknownFields() throws Exception {
        String json = """
                {"name":"Grace Hopper","age":85,"email":"grace@example.com","tags":[],"extra":true}
                """;

        Person person = demo.fromJson(json);

        assertEquals("Grace Hopper", person.name());
        assertEquals(85, person.age());
    }
}
