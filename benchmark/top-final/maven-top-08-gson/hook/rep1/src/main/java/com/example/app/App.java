package com.example.app;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class App {

    static class Person {
        String name;
        int age;

        Person(String name, int age) {
            this.name = name;
            this.age = age;
        }
    }

    public static void main(String[] args) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();

        Person person = new Person("Ada Lovelace", 36);
        String json = gson.toJson(person);
        System.out.println(json);

        Person parsed = gson.fromJson(json, Person.class);
        System.out.println(parsed.name + " is " + parsed.age + " years old.");
    }
}
