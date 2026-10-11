package com.example;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class GreeterTest {

    private final Greeter greeter = new Greeter();

    @Test
    void greetsByName() {
        assertEquals("Hello, World!", greeter.greet("World"));
    }

    @Test
    void fallsBackWhenNameIsBlank() {
        assertEquals("Hello, stranger!", greeter.greet("  "));
    }
}
