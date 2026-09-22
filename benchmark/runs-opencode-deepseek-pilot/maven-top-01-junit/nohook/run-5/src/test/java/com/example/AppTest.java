package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class AppTest {

    private App app;

    @BeforeEach
    void setUp() {
        app = new App();
    }

    @Test
    @DisplayName("add returns the sum of two integers")
    void addReturnsSum() {
        assertEquals(5, app.add(2, 3));
    }

    @Test
    void addHandlesNegativeNumbers() {
        assertEquals(-1, app.add(2, -3));
    }
}
