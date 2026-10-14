package com.example.json;

import java.util.List;

public class App {

    public static void main(String[] args) {
        Person person = new Person("Ada Lovelace", 36, List.of("ada@example.com"));

        String json = JsonCodec.toPrettyJson(person);
        System.out.println("Generated:\n" + json);

        Person parsed = JsonCodec.fromJson(json, Person.class);
        System.out.println("Parsed: " + parsed);
    }
}
