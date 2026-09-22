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
    @DisplayName("adds two positive numbers")
    void addsTwoNumbers() {
        assertEquals(5, calculator.add(2, 3));
    }

    @ParameterizedTest(name = "{0} + {1} = {2}")
    @CsvSource({"1, 1, 2", "-1, 1, 0", "0, 0, 0", "10, 20, 30"})
    void addsWithParameters(int a, int b, int expected) {
        assertEquals(expected, calculator.add(a, b));
    }

    @Test
    void subtractsTwoNumbers() {
        assertEquals(7, calculator.subtract(10, 3));
    }

    @Test
    void multipliesTwoNumbers() {
        assertEquals(42, calculator.multiply(6, 7));
    }

    @Test
    void dividesTwoNumbers() {
        assertEquals(3, calculator.divide(10, 3));
    }

    @Test
    void throwsWhenDividingByZero() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(1, 0));
    }
}
