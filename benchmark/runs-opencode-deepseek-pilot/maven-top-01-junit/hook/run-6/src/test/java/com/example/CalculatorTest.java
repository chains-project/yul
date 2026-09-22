package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class CalculatorTest {

    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    @Test
    @DisplayName("adds two numbers")
    void add() {
        assertEquals(4, calculator.add(2, 2));
    }

    @Test
    void subtract() {
        assertEquals(6, calculator.subtract(10, 4));
    }

    @ParameterizedTest
    @CsvSource({
            "2, 3, 6",
            "-2, 3, -6",
            "0, 5, 0"
    })
    void multiply(int a, int b, int expected) {
        assertEquals(expected, calculator.multiply(a, b));
    }

    @Test
    void divide() {
        assertEquals(5, calculator.divide(10, 2));
    }

    @Test
    void divideByZeroThrows() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.divide(1, 0));
        assertEquals("Cannot divide by zero", exception.getMessage());
    }
}
