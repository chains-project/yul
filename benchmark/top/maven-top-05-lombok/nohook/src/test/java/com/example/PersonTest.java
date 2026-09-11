package com.example;

import com.example.model.Person;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class PersonTest {

    @Test
    void generatedGettersAndConstructorWork() {
        Person person = new Person("Grace Hopper", 85, "grace@example.com");

        assertEquals("Grace Hopper", person.getName());
        assertEquals(85, person.getAge());
        assertEquals("grace@example.com", person.getEmail());
    }

    @Test
    void generatedSettersAndEqualsWork() {
        Person a = new Person();
        a.setName("Alan Turing");
        a.setAge(41);
        a.setEmail("alan@example.com");

        Person b = new Person("Alan Turing", 41, "alan@example.com");

        assertEquals(a, b);
    }
}
