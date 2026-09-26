package com.example.demo;

import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import static org.assertj.core.api.Assertions.assertThat;

class GreetingServiceTest {

    @Test
    void greetsWithName() {
        GreetingService service = Mockito.spy(new GreetingService());

        String result = service.greet("World");

        assertThat(result).isEqualTo("Hello, World!");
    }

}
