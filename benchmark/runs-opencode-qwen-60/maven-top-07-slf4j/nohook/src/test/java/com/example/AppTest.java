package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class AppTest {
    @Test
    public void testProcessWithValidInput() {
        App app = new App();
        String result = app.process("SLF4J");
        assertEquals("Hello from SLF4J!", result);
    }

    @Test
    public void testProcessWithNullInput() {
        App app = new App();
        String result = app.process(null);
        assertEquals("No input provided", result);
    }

    @Test
    public void testProcessWithEmptyInput() {
        App app = new App();
        String result = app.process("");
        assertEquals("No input provided", result);
    }
}