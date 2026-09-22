package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

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
    void addsPositiveNumbers() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    void subtractsNumbers() {
        assertEquals(1, calculator.subtract(3, 2));
    }

    @Test
    void multipliesNumbers() {
        assertEquals(12, calculator.multiply(3, 4));
    }

    @Test
    void dividesNumbers() {
        assertEquals(2, calculator.divide(6, 3));
    }

    @Test
    void throwsWhenDividingByZero() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(1, 0));
    }
}
