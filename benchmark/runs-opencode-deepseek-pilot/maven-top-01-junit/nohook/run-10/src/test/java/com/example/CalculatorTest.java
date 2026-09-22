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
    void add() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    @DisplayName("subtracts two numbers")
    void subtract() {
        assertEquals(-1, calculator.subtract(2, 3));
    }

    @Test
    @DisplayName("multiplies two numbers")
    void multiply() {
        assertEquals(6, calculator.multiply(2, 3));
    }

    @Test
    @DisplayName("divides two numbers")
    void divide() {
        assertEquals(2, calculator.divide(6, 3));
    }

    @Test
    @DisplayName("throws when dividing by zero")
    void divideByZero() {
        assertThrows(IllegalArgumentException.class, () -> calculator.divide(1, 0));
    }
}
