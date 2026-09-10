package com.example;

public class App {
    public int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        System.out.println(new App().add(2, 3));
    }
}
