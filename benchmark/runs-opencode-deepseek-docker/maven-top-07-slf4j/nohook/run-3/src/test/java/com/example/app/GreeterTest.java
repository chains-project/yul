package com.example.app;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class GreeterTest {

    private final Greeter greeter = new Greeter();

    @Test
    void greetsByName() {
        assertEquals("Hello, world!", greeter.greet("world"));
    }

    @Test
    void rejectsBlankName() {
        assertThrows(IllegalArgumentException.class, () -> greeter.greet(" "));
    }
}
