package com.example.app;

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
    void equalsAndHashCodeAreGenerated() {
        User a = new User(1L, "Ada Lovelace", "ada@example.com");
        User b = new User(1L, "Ada Lovelace", "ada@example.com");

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());
    }
}
