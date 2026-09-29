package com.example.jsondemo;

import java.util.List;

import com.example.jsondemo.model.Person;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

/**
 * Parses JSON into objects/trees and serializes objects back to JSON.
 */
public class JsonService {

    private final ObjectMapper mapper;

    public JsonService() {
        this.mapper = new ObjectMapper()
                .registerModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }

    /** Parse a JSON object into a {@link Person}. */
    public Person parsePerson(String json) throws JsonProcessingException {
        return mapper.readValue(json, Person.class);
    }

    /** Parse any JSON payload into a navigable tree. */
    public JsonNode parseTree(String json) throws JsonProcessingException {
        return mapper.readTree(json);
    }

    /** Serialize an object to a compact JSON string. */
    public String toJson(Object value) throws JsonProcessingException {
        return mapper.writeValueAsString(value);
    }

    /** Serialize an object to a pretty-printed JSON string. */
    public String toPrettyJson(Object value) throws JsonProcessingException {
        return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(value);
    }

    public static void main(String[] args) throws JsonProcessingException {
        JsonService service = new JsonService();

        String input = """
                {
                  "name": "Ada Lovelace",
                  "age": 36,
                  "email": "ada@example.com",
                  "roles": ["admin", "engineer"]
                }
                """;

        Person person = service.parsePerson(input);
        System.out.println("Parsed:  " + person);
        System.out.println("Name:    " + person.name());
        System.out.println("Roles:   " + person.roles());

        Person generated = new Person("Grace Hopper", 85,
                "grace@example.com", List.of("engineer", "author"));
        System.out.println("Generated JSON:");
        System.out.println(service.toPrettyJson(generated));
    }
}
