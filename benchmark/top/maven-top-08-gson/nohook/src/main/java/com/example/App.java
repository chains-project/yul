package com.example;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.util.List;

public class App {

    static class Person {
        String name;
        int age;
        List<String> emails;

        Person(String name, int age, List<String> emails) {
            this.name = name;
            this.age = age;
            this.emails = emails;
        }
    }

    public static void main(String[] args) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();

        Person person = new Person("Ada Lovelace", 36, List.of("ada@example.com"));

        String json = gson.toJson(person);
        System.out.println("Generated JSON:");
        System.out.println(json);

        Person parsed = gson.fromJson(json, Person.class);
        System.out.println("\nParsed back:");
        System.out.println(parsed.name + ", age " + parsed.age + ", emails " + parsed.emails);
    }
}
