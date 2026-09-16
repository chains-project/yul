package com.example.demo.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.Arrays;
import java.util.Collections;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class DemoServiceIntegrationTest {

    @Autowired
    private DemoService demoService;

    @Test
    @DisplayName("Integration: greet with valid name")
    void testGreetWithValidName() {
        String result = demoService.greet("Spring");
        assertEquals("Hello, Spring!", result);
    }

    @Test
    @DisplayName("Integration: greet with null name")
    void testGreetWithNullName() {
        String result = demoService.greet(null);
        assertEquals("Hello, Guest!", result);
    }

    @Test
    @DisplayName("Integration: getNames returns input list")
    void testGetNames() {
        var input = Arrays.asList("Alice", "Bob");
        var result = demoService.getNames(input);
        assertNotNull(result);
        assertEquals(2, result.size());
        assertEquals("Alice", result.get(0));
        assertEquals("Bob", result.get(1));
    }

    @Test
    @DisplayName("Integration: getNames with empty list")
    void testGetNamesEmpty() {
        var result = demoService.getNames(Collections.emptyList());
        assertNotNull(result);
        assertTrue(result.isEmpty());
    }
}