package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

/** Spring context test with a bean replaced by a Mockito mock. */
@SpringBootTest
class GreetingServiceSpringMockTest {

    @MockitoBean
    private GreetingRepository repository;

    @Autowired
    private GreetingService service;

    @Test
    void usesMockedRepositoryBean() {
        given(repository.findTemplate()).willReturn("Howdy, %s");

        assertThat(service.greet("Bob")).isEqualTo("Howdy, Bob");
    }
}
