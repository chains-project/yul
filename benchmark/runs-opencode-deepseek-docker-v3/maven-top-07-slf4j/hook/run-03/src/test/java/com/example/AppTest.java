package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class AppTest {

    @Test
    void greetReturnsPersonalizedMessage() {
        assertEquals("Hello, World!", new Greeter().greet("World"));
    }
}
