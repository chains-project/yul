package com.example.app;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class AppTest {

    @Test
    void greetReturnsGreeting() {
        assertEquals("Hello, world!", new App().greet("world"));
    }
}
