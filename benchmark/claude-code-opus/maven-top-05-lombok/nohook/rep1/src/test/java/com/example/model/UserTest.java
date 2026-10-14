package com.example.model;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class UserTest {

    @Test
    void lombokGeneratesAccessorsConstructorsAndBuilder() {
        User built = User.builder().id(1L).name("Ada").email("ada@example.com").build();
        User constructed = new User(1L, "Ada", "ada@example.com");

        assertEquals(built, constructed);
        assertEquals("Ada", built.getName());

        constructed.setName("Grace");
        assertEquals("Grace", constructed.getName());
    }

    @Test
    void valueClassIsImmutableWithGetters() {
        Address address = new Address("1 Main St", "Springfield");
        assertEquals("Springfield", address.getCity());
    }
}
