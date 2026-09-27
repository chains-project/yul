package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class DemoApplicationTests {

    @Autowired
    private GreetingService greetingService;

    @Test
    void contextLoads() {
        assertThat(greetingService).isNotNull();
    }

    @Test
    void greetingIsWiredThroughTheApplicationContext() {
        assertThat(greetingService.greet(2L)).isEqualTo("Hello, Bob!");
    }

}
