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
    @DisplayName("add returns the sum of two integers")
    void add() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    @DisplayName("subtract returns the difference of two integers")
    void subtract() {
        assertEquals(1, calculator.subtract(3, 2));
    }

    @Test
    @DisplayName("multiply returns the product of two integers")
    void multiply() {
        assertEquals(6, calculator.multiply(2, 3));
    }

    @Test
    @DisplayName("divide returns the quotient of two integers")
    void divide() {
        assertEquals(2, calculator.divide(6, 3));
    }

    @Test
    @DisplayName("divide throws when the divisor is zero")
    void divideByZero() {
        assertThrows(IllegalArgumentException.class, () -> calculator.divide(1, 0));
    }
}
