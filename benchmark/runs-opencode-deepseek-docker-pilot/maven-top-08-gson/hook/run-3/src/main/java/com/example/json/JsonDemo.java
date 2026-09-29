package com.example.json;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.util.List;

public final class JsonDemo {

    private final ObjectMapper mapper;

    public JsonDemo() {
        this.mapper = new ObjectMapper()
                .enable(SerializationFeature.INDENT_OUTPUT);
    }

    public String toJson(Person person) throws JsonProcessingException {
        return mapper.writeValueAsString(person);
    }

    public Person fromJson(String json) throws JsonProcessingException {
        return mapper.readValue(json, Person.class);
    }

    public static void main(String[] args) throws JsonProcessingException {
        JsonDemo demo = new JsonDemo();
        Person person = new Person(
                "Ada Lovelace",
                36,
                "ada@example.com",
                List.of("mathematician", "programmer"));

        String json = demo.toJson(person);
        System.out.println("Generated JSON:");
        System.out.println(json);

        Person parsed = demo.fromJson(json);
        System.out.println("Parsed object: " + parsed);
    }
}
