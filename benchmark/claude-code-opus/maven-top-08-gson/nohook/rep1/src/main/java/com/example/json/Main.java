package com.example.json;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        var person = new Person("Ada", 36, List.of("ada@example.com"));

        String json = Json.writePretty(person);
        System.out.println(json);

        Person parsed = Json.parse(json, Person.class);
        System.out.println(parsed);
    }
}
