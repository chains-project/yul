package com.example.app;

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
    void generatedSettersAndEqualsWork() {
        User a = new User();
        a.setId(7L);
        a.setName("Grace Hopper");

        User b = new User(7L, "Grace Hopper", null);

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());

        b.setName("Someone Else");
        assertNotEquals(a, b);
    }
}
