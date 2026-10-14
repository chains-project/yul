package com.example.json;

import java.util.List;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.node.ObjectNode;

public class App {

    public static void main(String[] args) {
        // Object -> JSON
        Person alice = new Person("Alice", 30, List.of("admin", "dev"));
        System.out.println(Json.writePretty(alice));

        // JSON -> object
        Person bob = Json.parse("{\"name\":\"Bob\",\"age\":25,\"tags\":[\"ops\"]}", Person.class);
        System.out.println(bob);

        // Tree model for ad-hoc JSON
        JsonNode node = Json.parseTree("{\"user\":{\"id\":42}}");
        System.out.println("user.id = " + node.at("/user/id").asInt());

        ObjectNode built = Json.mapper().createObjectNode()
                .put("status", "ok")
                .put("count", 3);
        System.out.println(Json.write(built));
    }
}
