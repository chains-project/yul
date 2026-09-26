package com.example.app;

import com.google.gson.Gson;

public class App {
    public static void main(String[] args) {
        Gson gson = new Gson();

        Person person = new Person("Ada Lovelace", 36);
        String json = gson.toJson(person);
        System.out.println("Generated JSON: " + json);

        Person parsed = gson.fromJson(json, Person.class);
        System.out.println("Parsed back: " + parsed.getName() + ", age " + parsed.getAge());
    }
}
