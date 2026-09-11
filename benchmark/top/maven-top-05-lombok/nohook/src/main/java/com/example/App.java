package com.example;

import com.example.model.Person;

public class App {
    public static void main(String[] args) {
        Person person = new Person("Ada Lovelace", 36, "ada@example.com");
        System.out.println(person);
    }
}
