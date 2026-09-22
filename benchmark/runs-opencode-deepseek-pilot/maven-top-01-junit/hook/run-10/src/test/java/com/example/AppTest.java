package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class AppTest {

    private final App app = new App();

    @Test
    void addReturnsSum() {
        assertEquals(5, app.add(2, 3));
    }
}
