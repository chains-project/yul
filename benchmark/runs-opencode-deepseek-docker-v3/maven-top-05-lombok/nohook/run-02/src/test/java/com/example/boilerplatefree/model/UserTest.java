package com.example.boilerplatefree.model;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class UserTest {

    @Test
    void builderPopulatesGetters() {
        User user = User.builder()
                .id(1L)
                .username("ada")
                .roles(List.of("USER"))
                .build();

        assertEquals("ada", user.getUsername());
        assertTrue(user.getRoles().contains("USER"));
    }

    @Test
    void equalsUsesIdOnly() {
        User a = User.builder().id(1L).username("ada").build();
        User b = User.builder().id(1L).username("someone-else").build();
        User c = User.builder().id(2L).username("ada").build();

        assertEquals(a, b);
        assertNotEquals(a, c);
    }
}
