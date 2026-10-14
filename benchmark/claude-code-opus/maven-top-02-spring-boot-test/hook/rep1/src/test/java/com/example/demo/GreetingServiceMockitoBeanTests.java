package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

/** Loads the Spring context but replaces a bean with a Mockito mock. */
@SpringBootTest
class GreetingServiceMockitoBeanTests {

    @MockitoBean
    private GreetingRepository repository;

    @Autowired
    private GreetingService greetingService;

    @Test
    void usesMockedRepository() {
        given(repository.findTemplate()).willReturn("Hi, %s");

        assertThat(greetingService.greet("Spring")).isEqualTo("Hi, Spring");
    }
}
