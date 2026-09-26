package com.example.demo;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class GreetingServiceTests {

    private final GreetingService greetingService = new GreetingService();

    @Test
    void greetReturnsPersonalizedMessage() {
        assertThat(greetingService.greet("Alice")).isEqualTo("Hello, Alice!");
    }
}
