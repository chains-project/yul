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
    @DisplayName("add returns the sum of two numbers")
    void add() {
        assertEquals(4, calculator.add(2, 2));
    }

    @Test
    void subtract() {
        assertEquals(1, calculator.subtract(3, 2));
    }

    @Test
    void multiply() {
        assertEquals(6, calculator.multiply(2, 3));
    }

    @Test
    void divide() {
        assertEquals(2, calculator.divide(6, 3));
    }

    @Test
    void divideByZeroThrows() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(1, 0));
    }
}
