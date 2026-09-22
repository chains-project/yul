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
    @DisplayName("adds two numbers")
    void addsTwoNumbers() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    @DisplayName("subtracts two numbers")
    void subtractsTwoNumbers() {
        assertEquals(-1, calculator.subtract(2, 3));
    }

    @Test
    @DisplayName("multiplies two numbers")
    void multipliesTwoNumbers() {
        assertEquals(6, calculator.multiply(2, 3));
    }

    @Test
    @DisplayName("divides two numbers")
    void dividesTwoNumbers() {
        assertEquals(2, calculator.divide(6, 3));
    }

    @Test
    @DisplayName("throws when dividing by zero")
    void throwsWhenDividingByZero() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(1, 0));
    }
}
