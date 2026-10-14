package com.example.json;

import java.util.List;

import tools.jackson.databind.JsonNode;

public class App {

    public static void main(String[] args) {
        Person alice = new Person("Alice", 30, List.of("admin", "dev"));

        String json = Json.toPrettyJson(alice);
        System.out.println("Generated:\n" + json);

        Person parsed = Json.fromJson(json, Person.class);
        System.out.println("Parsed record: " + parsed);

        JsonNode tree = Json.parseTree("{\"name\":\"Bob\",\"age\":25,\"tags\":[\"ops\"]}");
        System.out.println("Tree lookup: " + tree.get("name").asString() + " is " + tree.get("age").asInt());
    }
}
