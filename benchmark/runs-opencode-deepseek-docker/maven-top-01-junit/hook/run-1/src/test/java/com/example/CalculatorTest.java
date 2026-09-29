package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class CalculatorTest {

    private final Calculator calculator = new Calculator();

    @Test
    void addsTwoNumbers() {
        assertEquals(4, calculator.add(2, 2));
    }
}
