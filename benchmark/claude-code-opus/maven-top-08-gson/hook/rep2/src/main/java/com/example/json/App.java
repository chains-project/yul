package com.example.json;

import java.util.List;

public class App {

    public static void main(String[] args) {
        Person alice = new Person("Alice", 30, List.of("admin", "dev"));

        String json = Json.writePretty(alice);
        System.out.println("Generated:\n" + json);

        Person parsed = Json.parse(json, Person.class);
        System.out.println("Parsed: " + parsed);
    }
}
