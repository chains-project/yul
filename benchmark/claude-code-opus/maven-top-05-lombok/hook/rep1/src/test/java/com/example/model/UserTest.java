package com.example.model;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void lombokGeneratesAccessorsConstructorsAndBuilder() {
        User built = User.builder().id(1L).name("Ada").email("ada@example.com").build();
        User constructed = new User(1L, "Ada", "ada@example.com");

        User mutable = new User();
        mutable.setId(1L);
        mutable.setName("Ada");
        mutable.setEmail("ada@example.com");

        assertEquals("Ada", built.getName());
        assertEquals(built, constructed);
        assertEquals(built, mutable);
    }
}
