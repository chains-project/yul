package com.example.app.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void builderCreatesFullyPopulatedInstance() {
        User user = User.builder()
                .id(1L)
                .username("jane")
                .email("jane@example.com")
                .build();

        assertEquals("jane", user.getUsername());
        assertEquals("jane@example.com", user.getEmail());
    }

    @Test
    void settersAndGettersWork() {
        User user = new User();
        assertNull(user.getUsername());

        user.setUsername("john");

        assertEquals("john", user.getUsername());
    }

    @Test
    void equalsAndHashCodeAreGenerated() {
        User a = User.builder().id(1L).username("jane").build();
        User b = User.builder().id(1L).username("jane").build();
        User c = User.builder().id(2L).username("jane").build();

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());
        assertNotEquals(a, c);
    }
}
