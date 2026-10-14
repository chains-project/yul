package com.example.json;

import java.util.List;

public class App {
    public static void main(String[] args) {
        Person person = JsonCodec.parse("{\"name\":\"Ada\",\"age\":36,\"tags\":[\"math\"]}", Person.class);
        System.out.println("Parsed: " + person);

        Person updated = new Person(person.name(), person.age() + 1, List.of("math", "computing"));
        System.out.println("Generated:\n" + JsonCodec.toPrettyJson(updated));
    }
}
