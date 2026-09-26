package com.example.app;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PersonTest {

    @Test
    void generatedAccessorsWork() {
        Person person = new Person("Ada", 30);
        assertEquals("Ada", person.getName());
        assertEquals(30, person.getAge());

        person.setAge(31);
        assertEquals(31, person.getAge());
    }

    @Test
    void noArgsConstructorWorks() {
        Person person = new Person();
        person.setName("Grace");
        assertEquals("Grace", person.getName());
    }
}
