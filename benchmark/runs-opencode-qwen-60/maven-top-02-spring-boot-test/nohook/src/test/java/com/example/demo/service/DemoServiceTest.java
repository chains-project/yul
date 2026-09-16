package com.example.demo.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.Mockito;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class DemoServiceTest {

    private DemoService demoService;

    @BeforeEach
    void setUp() {
        demoService = new DemoService();
    }

    @Test
    @DisplayName("Should greet a named person")
    void testGreetWithValidName() {
        String result = demoService.greet("World");
        assertEquals("Hello, World!", result);
    }

    @Test
    @DisplayName("Should greet guest when name is null")
    void testGreetWithNullName() {
        String result = demoService.greet(null);
        assertEquals("Hello, Guest!", result);
    }

    @Test
    @DisplayName("Should greet guest when name is blank")
    void testGreetWithBlankName() {
        String result = demoService.greet("   ");
        assertEquals("Hello, Guest!", result);
    }
}