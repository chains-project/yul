package com.example.demo.model;

import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class UserTest {

    @Test
    void builderPopulatesAllFields() {
        Instant now = Instant.now();
        User user = User.builder()
                .id(1L)
                .username("alice")
                .email("alice@example.com")
                .createdAt(now)
                .build();

        assertEquals(1L, user.getId());
        assertEquals("alice", user.getUsername());
        assertEquals("alice@example.com", user.getEmail());
        assertEquals(now, user.getCreatedAt());
    }

    @Test
    void settersAndGettersAreGenerated() {
        User user = new User();
        user.setId(2L);
        user.setUsername("bob");

        assertEquals(2L, user.getId());
        assertEquals("bob", user.getUsername());
    }

    @Test
    void equalsAndHashCodeAreValueBased() {
        User a = User.builder().id(1L).username("alice").build();
        User b = User.builder().id(1L).username("alice").build();
        User c = User.builder().id(2L).username("bob").build();

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());
        assertNotEquals(a, c);
    }

    @Test
    void toStringIsGenerated() {
        User user = User.builder().id(1L).username("alice").build();
        assertNotNull(user.toString());
        assertTrue(user.toString().contains("alice"));
    }
}
