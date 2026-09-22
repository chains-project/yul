package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class CalculatorTest {

    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    @Test
    @DisplayName("adds two positive numbers")
    void add() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    @DisplayName("subtracts two numbers")
    void subtract() {
        assertEquals(1, calculator.subtract(3, 2));
    }
}
