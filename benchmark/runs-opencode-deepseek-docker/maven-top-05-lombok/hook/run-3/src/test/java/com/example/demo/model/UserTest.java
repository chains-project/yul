package com.example.demo.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void builderAndAccessorsWork() {
        User user = User.builder()
                .id(1L)
                .username("ada")
                .email("ada@example.com")
                .build();

        assertEquals("ada", user.getUsername());
        assertEquals("ada@example.com", user.getEmail());

        user.setEmail("ada.lovelace@example.com");
        assertEquals("ada.lovelace@example.com", user.getEmail());
    }

    @Test
    void equalsAndHashCodeAreGenerated() {
        User a = User.builder().id(1L).username("ada").build();
        User b = User.builder().id(1L).username("ada").build();
        User c = User.builder().id(2L).username("ada").build();

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());
        assertNotEquals(a, c);
    }
}
