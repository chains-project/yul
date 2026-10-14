package com.example.app.model;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void lombokGeneratesAccessorsConstructorsAndBuilder() {
        User viaBuilder = User.builder().id(1L).name("Ada").email("ada@example.com").build();
        User viaConstructor = new User(1L, "Ada", "ada@example.com");

        assertEquals(viaConstructor, viaBuilder);

        viaBuilder.setName("Grace");
        assertEquals("Grace", viaBuilder.getName());
    }
}
