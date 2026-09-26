package com.example.app;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class AppTest {
    @Test
    void addsTwoNumbers() {
        assertEquals(5, new App().add(2, 3));
    }
}
