package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class AppTest {
    private final App app = new App();

    @Test
    void addReturnsSumOfOperands() {
        assertEquals(4, app.add(2, 2));
    }

    @Test
    void addHandlesNegativeNumbers() {
        assertEquals(-1, app.add(2, -3));
    }
}
