package com.example.app;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class UserTest {

    @Test
    void gettersSettersAndEqualsAreGeneratedByLombok() {
        User user = new User(1L, "Ada Lovelace", "ada@example.com");

        assertEquals(1L, user.getId());
        assertEquals("Ada Lovelace", user.getName());
        assertEquals("ada@example.com", user.getEmail());

        User sameUser = new User(1L, "Ada Lovelace", "ada@example.com");
        assertEquals(user, sameUser);
    }
}
