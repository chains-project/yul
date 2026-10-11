package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

@SpringBootTest
class DemoApplicationTests {

    @Autowired
    private GreetingService greetingService;

    @MockitoBean
    private PrefixProvider prefixProvider;

    @Test
    void contextLoads() {
        assertThat(greetingService).isNotNull();
    }

    @Test
    void greetingUsesTheSpringManagedAndMockedBean() {
        given(prefixProvider.prefix()).willReturn("Hi");

        assertThat(greetingService.greet("Spring"))
                .isEqualTo("Hi, Spring!");
    }
}
