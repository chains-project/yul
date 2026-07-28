package com.example.app;

import com.fasterxml.jackson.databind.ObjectMapper;

public class App {

    public record Person(String name, int age) {}

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        Person person = new Person("Ada Lovelace", 36);
        String json = mapper.writeValueAsString(person);
        System.out.println("Generated JSON: " + json);

        Person parsed = mapper.readValue(json, Person.class);
        System.out.println("Parsed back: " + parsed);
    }
}
