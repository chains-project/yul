package com.example.json;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

public class JsonApp {

    private final ObjectMapper mapper;

    public JsonApp() {
        this.mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
    }

    public String toJson(User user) throws Exception {
        return mapper.writeValueAsString(user);
    }

    public User fromJson(String json) throws Exception {
        return mapper.readValue(json, User.class);
    }

    public static void main(String[] args) throws Exception {
        JsonApp app = new JsonApp();

        User user = new User(1L, "Ada Lovelace", "ada@example.com");

        String json = app.toJson(user);
        System.out.println("Generated JSON:");
        System.out.println(json);

        User parsed = app.fromJson(json);
        System.out.println("Parsed object: " + parsed);
    }
}
