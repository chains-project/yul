package com.example.app;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

class AppTest {

    @Test
    void mainRunsWithoutThrowing() {
        assertDoesNotThrow(() -> App.main(new String[] {}));
    }
}
