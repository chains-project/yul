package com.example.json;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;

public final class App {

    private final ObjectMapper mapper;

    public App() {
        this.mapper = new ObjectMapper();
    }

    public App(ObjectMapper mapper) {
        this.mapper = mapper;
    }

    public String toJson(Person person) throws Exception {
        return mapper.writeValueAsString(person);
    }

    public Person fromJson(String json) throws Exception {
        return mapper.readValue(json, Person.class);
    }

    public String prettyJson(String json) throws Exception {
        JsonNode node = mapper.readTree(json);
        return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(node);
    }

    public static void main(String[] args) throws Exception {
        App app = new App();

        Person person = new Person("Ada Lovelace", 36, List.of("mathematics", "programming"));
        String json = app.toJson(person);
        System.out.println("Generated: " + json);

        Person parsed = app.fromJson(json);
        System.out.println("Parsed:    " + parsed);

        System.out.println("Pretty:");
        System.out.println(app.prettyJson("{\"name\":\"Ada\",\"age\":36,\"hobbies\":[\"math\"]}"));
    }
}
