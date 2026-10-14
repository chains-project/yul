package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

@SpringBootTest
class GreetingServiceMockBeanTests {

    @MockitoBean
    private GreetingRepository repository;

    @Autowired
    private GreetingService greetingService;

    @Test
    void greetUsesMockedBeanInSpringContext() {
        given(repository.findTemplate()).willReturn("Hey, %s");

        assertThat(greetingService.greet("Bob")).isEqualTo("Hey, Bob");
    }
}
