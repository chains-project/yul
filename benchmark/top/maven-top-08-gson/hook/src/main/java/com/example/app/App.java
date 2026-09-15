package com.example.app;

import com.google.gson.Gson;

public class App {

    public static class Person {
        String name;
        int age;

        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }
    }

    public static void main(String[] args) {
        Gson gson = new Gson();

        Person person = new Person("Ada Lovelace", 36);
        String json = gson.toJson(person);
        System.out.println("Serialized: " + json);

        Person parsed = gson.fromJson(json, Person.class);
        System.out.println("Deserialized: " + parsed.name + ", " + parsed.age);
    }
}
