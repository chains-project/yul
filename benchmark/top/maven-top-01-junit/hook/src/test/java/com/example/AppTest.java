package com.example;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class AppTest {
    @Test
    void addsTwoNumbers() {
        assertEquals(5, new App().add(2, 3));
    }
}
