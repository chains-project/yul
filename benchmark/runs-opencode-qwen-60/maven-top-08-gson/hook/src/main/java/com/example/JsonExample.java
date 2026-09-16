package com.example;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class JsonExample {

    private String name;
    private int age;
    private String email;

    public JsonExample() {}

    public JsonExample(String name, int age, String email) {
        this.name = name;
        this.age = age;
        this.email = email;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public static void main(String[] args) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();

        // Generate JSON from Java object
        JsonExample person = new JsonExample("John Doe", 30, "john@example.com");
        String jsonOutput = gson.toJson(person);
        System.out.println("Generated JSON:");
        System.out.println(jsonOutput);

        // Parse JSON into Java object
        String jsonString = "{\"name\":\"Jane Smith\",\"age\":25,\"email\":\"jane@example.com\"}";
        System.out.println("\nParsing JSON:");
        JsonExample parsed = gson.fromJson(jsonString, JsonExample.class);
        System.out.println("Parsed - Name: " + parsed.getName() + ", Age: " + parsed.getAge() + ", Email: " + parsed.getEmail());

        // Parse raw JSON string
        JsonObject obj = JsonParser.parseString(jsonString).getAsJsonObject();
        System.out.println("\nRaw JSON parse - Name: " + obj.get("name").getAsString());
    }
}