package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

@SpringBootTest
class DemoApplicationTests {

    @Autowired
    private GreetingService greetingService;

    @MockitoBean
    private MessageProvider messageProvider;

    @Test
    void contextLoads() {
        assertThat(greetingService).isNotNull();
    }

    @Test
    void greetingUsesStubbedBean() {
        given(messageProvider.getMessage()).willReturn("Welcome");

        assertThat(greetingService.greet("Spring")).isEqualTo("Welcome, Spring!");
    }
}
