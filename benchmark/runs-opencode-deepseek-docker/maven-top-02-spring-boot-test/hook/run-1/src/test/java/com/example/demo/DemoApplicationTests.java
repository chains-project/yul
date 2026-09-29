package com.example.demo;

import com.example.demo.greeting.GreetingService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Loads the full Spring application context.
 */
@SpringBootTest
class DemoApplicationTests {

    @Autowired
    private GreetingService greetingService;

    @Test
    void contextLoads() {
        assertThat(this.greetingService).isNotNull();
    }

    @Test
    void greetsUsingTheRealRepository() {
        assertThat(this.greetingService.greet(1L)).isEqualTo("Hello, World!");
    }

}
