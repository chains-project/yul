package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class AppTest {

    @Test
    void greetReturnsExpectedMessage() {
        App app = new App();
        assertEquals("Hello, world!", app.greet("world"));
    }

    @Test
    void loggerResolvesFromFacade() {
        Logger log = LoggerFactory.getLogger(App.class);
        assertNotNull(log);
    }
}
