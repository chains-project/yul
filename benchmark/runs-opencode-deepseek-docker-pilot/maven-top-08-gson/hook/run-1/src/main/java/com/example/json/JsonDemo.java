package com.example.json;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;

public final class JsonDemo {

    private final ObjectMapper mapper;

    public JsonDemo() {
        this(new ObjectMapper());
    }

    public JsonDemo(ObjectMapper mapper) {
        this.mapper = mapper;
    }

    public String toJson(Person person) throws JsonProcessingException {
        return mapper.writeValueAsString(person);
    }

    public Person fromJson(String json) throws JsonProcessingException {
        return mapper.readValue(json, Person.class);
    }

    public JsonNode readTree(String json) throws JsonProcessingException {
        return mapper.readTree(json);
    }

    public record Person(String name, int age, List<String> hobbies) {
    }

    public static void main(String[] args) throws JsonProcessingException {
        JsonDemo demo = new JsonDemo();
        Person person = new Person("Ada", 36, List.of("mathematics", "computing"));

        String json = demo.toJson(person);
        System.out.println("Generated: " + json);

        Person parsed = demo.fromJson(json);
        System.out.println("Parsed: " + parsed.name() + " (" + parsed.age() + ")");

        JsonNode tree = demo.readTree(json);
        System.out.println("First hobby: " + tree.path("hobbies").path(0).asText());
    }
}
