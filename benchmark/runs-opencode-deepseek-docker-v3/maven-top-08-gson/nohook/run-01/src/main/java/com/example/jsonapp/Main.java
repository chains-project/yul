package com.example.jsonapp;

import com.example.jsonapp.model.Person;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.Instant;
import java.util.List;

public final class Main {

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = JsonMapperFactory.create();

        Person person = new Person(
                1L,
                "Ada Lovelace",
                "ada@example.com",
                Instant.parse("2026-01-01T00:00:00Z"),
                List.of("admin", "user"));

        String json = mapper
                .writerWithDefaultPrettyPrinter()
                .writeValueAsString(person);
        System.out.println("Generated JSON:");
        System.out.println(json);

        Person parsed = mapper.readValue(json, Person.class);
        System.out.println("Parsed back: " + parsed);
    }
}
