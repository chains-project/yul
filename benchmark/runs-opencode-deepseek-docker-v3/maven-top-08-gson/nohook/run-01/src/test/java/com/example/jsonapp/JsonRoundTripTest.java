package com.example.jsonapp;

import com.example.jsonapp.model.Person;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class JsonRoundTripTest {

    private final ObjectMapper mapper = JsonMapperFactory.create();

    @Test
    void generatesAndParsesJson() throws Exception {
        Person original = new Person(
                1L,
                "Ada Lovelace",
                "ada@example.com",
                Instant.parse("2026-01-01T00:00:00Z"),
                List.of("admin", "user"));

        String json = mapper.writeValueAsString(original);
        Person parsed = mapper.readValue(json, Person.class);

        assertEquals(original, parsed);
    }
}
