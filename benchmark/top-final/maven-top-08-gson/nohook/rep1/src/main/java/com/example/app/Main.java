package com.example.app;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();

        Person person = new Person("Ada Lovelace", 36, List.of("ada@example.com"));
        String json = gson.toJson(person);
        System.out.println("Generated JSON:");
        System.out.println(json);

        Person parsed = gson.fromJson(json, Person.class);
        System.out.println("Parsed back:");
        System.out.println(parsed);
    }
}
