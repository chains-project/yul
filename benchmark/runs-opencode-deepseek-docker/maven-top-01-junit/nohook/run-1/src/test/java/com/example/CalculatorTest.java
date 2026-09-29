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
    void addReturnsSum() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    @DisplayName("subtract returns the difference of two numbers")
    void subtractReturnsDifference() {
        assertEquals(1, calculator.subtract(3, 2));
    }

    @Test
    @DisplayName("multiply returns the product of two numbers")
    void multiplyReturnsProduct() {
        assertEquals(12, calculator.multiply(3, 4));
    }

    @Test
    @DisplayName("divide throws when the divisor is zero")
    void divideByZeroThrows() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(1, 0));
    }
}
