package com.example.app;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Map;

public class App {
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        Map<String, Object> data = Map.of("name", "example", "count", 42);
        String json = mapper.writeValueAsString(data);
        System.out.println("Generated: " + json);

        Map<?, ?> parsed = mapper.readValue(json, Map.class);
        System.out.println("Parsed back: " + parsed);
    }
}
