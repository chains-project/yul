package com.example.jsondemo;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

public class App {

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        mapper.enable(SerializationFeature.INDENT_OUTPUT);

        User user = new User(1L, "Ada Lovelace", "ada@example.com");

        String json = mapper.writeValueAsString(user);
        System.out.println("Generated JSON:");
        System.out.println(json);

        User parsed = mapper.readValue(json, User.class);
        System.out.println("Parsed back: " + parsed);
    }
}
