package com.example.app.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

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
}
