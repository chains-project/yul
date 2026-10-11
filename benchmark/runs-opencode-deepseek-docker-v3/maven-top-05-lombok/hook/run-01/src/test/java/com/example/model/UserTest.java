package com.example.model;

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
        User third = new User(2L, "Grace", "grace@example.com");

        assertEquals(first, second);
        assertEquals(first.hashCode(), second.hashCode());
        assertNotEquals(first, third);
    }

    @Test
    void settersMutateFields() {
        User user = new User();

        user.setId(7L);
        user.setName("Grace Hopper");

        assertEquals(7L, user.getId());
        assertEquals("Grace Hopper", user.getName());
    }
}
