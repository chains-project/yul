package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class CalculatorTest {

    private final Calculator calculator = new Calculator();

    @Test
    void addReturnsSum() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    void subtractReturnsDifference() {
        assertEquals(1, calculator.subtract(3, 2));
    }

    @Test
    void divideReturnsQuotient() {
        assertEquals(2, calculator.divide(6, 3));
    }

    @Test
    void divideByZeroThrows() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(1, 0));
    }
}
