package com.example.demo.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.time.Instant;
import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void builderAndAccessorsWork() {
        Instant now = Instant.now();
        User user = User.builder()
                .id(1L)
                .username("ada")
                .email("ada@example.com")
                .createdAt(now)
                .build();

        assertEquals(1L, user.getId());
        assertEquals("ada", user.getUsername());
        assertEquals("ada@example.com", user.getEmail());
        assertEquals(now, user.getCreatedAt());
    }

    @Test
    void settersAndEqualsWork() {
        User a = new User();
        a.setId(1L);
        a.setUsername("ada");

        User b = new User();
        b.setId(1L);
        b.setUsername("ada");

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());

        b.setUsername("grace");
        assertNotEquals(a, b);
    }
}
