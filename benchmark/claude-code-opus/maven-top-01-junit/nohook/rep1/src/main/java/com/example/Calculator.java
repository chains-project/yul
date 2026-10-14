package com.example;

public class Calculator {

    public int add(int a, int b) {
        return a + b;
    }

    public int divide(int dividend, int divisor) {
        if (divisor == 0) {
            throw new IllegalArgumentException("divisor must not be zero");
        }
        return dividend / divisor;
    }
}
