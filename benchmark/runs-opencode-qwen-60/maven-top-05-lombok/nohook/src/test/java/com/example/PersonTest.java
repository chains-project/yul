package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class PersonTest {

    @Test
    public void testBuilder() {
        Person person = Person.builder()
                .name("John Doe")
                .age(30)
                .email("john@example.com")
                .build();

        assertEquals("John Doe", person.getName());
        assertEquals(30, person.getAge());
        assertEquals("john@example.com", person.getEmail());
    }

    @Test
    public void testAllArgsConstructor() {
        Person person = new Person("Jane Doe", 25, "jane@example.com");

        assertEquals("Jane Doe", person.getName());
        assertEquals(25, person.getAge());
        assertEquals("jane@example.com", person.getEmail());
    }

    @Test
    public void testEqualsAndHashCode() {
        Person person1 = new Person("Alice", 20, "alice@example.com");
        Person person2 = new Person("Alice", 20, "alice@example.com");

        assertEquals(person1, person2);
        assertEquals(person1.hashCode(), person2.hashCode());
    }

    @Test
    public void testToString() {
        Person person = new Person("Bob", 35, "bob@example.com");
        String str = person.toString();

        assertTrue(str.contains("Bob"));
        assertTrue(str.contains("35"));
        assertTrue(str.contains("bob@example.com"));
    }

    @Test
    public void testSetters() {
        Person person = new Person("Charlie", 40, "charlie@example.com");
        person.setName("Charles");
        person.setAge(41);
        person.setEmail("charles@example.com");

        assertEquals("Charles", person.getName());
        assertEquals(41, person.getAge());
        assertEquals("charles@example.com", person.getEmail());
    }
}