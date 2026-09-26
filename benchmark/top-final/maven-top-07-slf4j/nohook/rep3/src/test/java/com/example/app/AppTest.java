package com.example.app;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class AppTest {
    @Test
    void greetReturnsExpectedMessage() {
        assertEquals("Hello, world!", new App().greet("world"));
    }
}
