package com.example.demo.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.util.List;
import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void builderAndAccessorsWork() {
        User user = User.builder()
                .id(1L)
                .name("Ada")
                .email("ada@example.com")
                .roles(List.of("admin"))
                .build();

        assertEquals(1L, user.getId());
        assertEquals("Ada", user.getName());
        assertEquals("ada@example.com", user.getEmail());
        assertEquals(List.of("admin"), user.getRoles());
    }

    @Test
    void equalsAndHashCodeAreGenerated() {
        User a = User.builder().id(1L).name("Ada").build();
        User b = User.builder().id(1L).name("Ada").build();
        User c = User.builder().id(2L).name("Ada").build();

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());
        assertNotEquals(a, c);
    }
}
