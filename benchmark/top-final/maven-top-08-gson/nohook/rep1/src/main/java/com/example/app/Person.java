package com.example.app;

import java.util.List;

public class Person {
    private String name;
    private int age;
    private List<String> emails;

    public Person(String name, int age, List<String> emails) {
        this.name = name;
        this.age = age;
        this.emails = emails;
    }

    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }

    public List<String> getEmails() {
        return emails;
    }

    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + ", emails=" + emails + "}";
    }
}
