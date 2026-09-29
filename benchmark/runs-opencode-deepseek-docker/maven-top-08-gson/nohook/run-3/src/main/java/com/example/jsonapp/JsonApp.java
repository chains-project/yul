package com.example.jsonapp;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;

public final class JsonApp {

    private final ObjectMapper mapper;

    public JsonApp() {
        this(new ObjectMapper());
    }

    public JsonApp(ObjectMapper mapper) {
        this.mapper = mapper;
    }

    public String toJson(Person person) throws JsonProcessingException {
        return mapper.writeValueAsString(person);
    }

    public Person fromJson(String json) throws JsonProcessingException {
        return mapper.readValue(json, Person.class);
    }

    public static void main(String[] args) throws JsonProcessingException {
        JsonApp app = new JsonApp();

        Person person = new Person("Ada Lovelace", 36, List.of("mathematics", "programming"));
        String json = app.toJson(person);
        System.out.println("Generated JSON: " + json);

        Person parsed = app.fromJson(json);
        System.out.println("Parsed person: " + parsed);
    }
}
