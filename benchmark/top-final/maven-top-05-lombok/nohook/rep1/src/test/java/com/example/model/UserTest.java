package com.example.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class UserTest {

    @Test
    void gettersAndSettersWork() {
        User user = new User();
        user.setId(1L);
        user.setName("Ada Lovelace");
        user.setEmail("ada@example.com");

        assertEquals(1L, user.getId());
        assertEquals("Ada Lovelace", user.getName());
        assertEquals("ada@example.com", user.getEmail());
    }

    @Test
    void allArgsConstructorWorks() {
        User user = new User(2L, "Grace Hopper", "grace@example.com");
        assertEquals(new User(2L, "Grace Hopper", "grace@example.com"), user);
    }
}
