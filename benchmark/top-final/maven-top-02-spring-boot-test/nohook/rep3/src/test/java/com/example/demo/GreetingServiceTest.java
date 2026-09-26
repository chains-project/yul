package com.example.demo;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class GreetingServiceTest {

    private final GreetingService greetingService = new GreetingService();

    @Test
    void greetReturnsGreetingWithName() {
        String result = greetingService.greet("World");

        assertThat(result).isEqualTo("Hello, World!");
    }

}
