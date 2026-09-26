package com.example.app;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class UserTest {

    @Test
    void gettersAndSettersWorkViaLombok() {
        User user = new User();
        user.setName("Ada Lovelace");
        user.setEmail("ada@example.com");
        user.setAge(30);

        assertEquals("Ada Lovelace", user.getName());
        assertEquals("ada@example.com", user.getEmail());
        assertEquals(30, user.getAge());
    }

    @Test
    void allArgsConstructorAndEqualsWork() {
        User a = new User("Ada Lovelace", "ada@example.com", 30);
        User b = new User("Ada Lovelace", "ada@example.com", 30);

        assertEquals(a, b);
    }
}
