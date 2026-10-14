package com.example.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;
import tools.jackson.core.JacksonException;

class JsonTest {

    @Test
    void roundTripsRecord() {
        var person = new Person("Ada", 36, List.of("ada@example.com"));
        assertEquals(person, Json.parse(Json.write(person), Person.class));
    }

    @Test
    void writesExpectedJson() {
        var person = new Person("Ada", 36, List.of());
        assertEquals("{\"name\":\"Ada\",\"age\":36,\"emails\":[]}", Json.write(person));
    }

    @Test
    void parsesTree() {
        var node = Json.parseTree("{\"a\":{\"b\":[1,2,3]}}");
        assertEquals(3, node.path("a").path("b").get(2).asInt());
    }

    @Test
    void rejectsMalformedJson() {
        assertThrows(JacksonException.class, () -> Json.parseTree("{not json"));
    }
}
