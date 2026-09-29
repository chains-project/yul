package com.example.app.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void builderPopulatesAllFields() {
        User user = User.builder()
                .id(1L)
                .name("Ada Lovelace")
                .email("ada@example.com")
                .build();

        assertEquals(1L, user.getId());
        assertEquals("Ada Lovelace", user.getName());
        assertEquals("ada@example.com", user.getEmail());
    }

    @Test
    void equalsAndHashCodeAreGenerated() {
        User first = new User(1L, "Ada", "ada@example.com");
        User second = new User(1L, "Ada", "ada@example.com");

        assertEquals(first, second);
        assertEquals(first.hashCode(), second.hashCode());
    }

    @Test
    void settersAreGenerated() {
        User user = new User();
        user.setName("Grace Hopper");

        assertEquals("Grace Hopper", user.getName());
        assertNotEquals("Ada", user.getName());
    }
}
