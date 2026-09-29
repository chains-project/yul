package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

@SpringBootTest
class GreetingServiceContextTest {

    @MockitoBean
    private GreetingRepository greetingRepository;

    @Autowired
    private GreetingService greetingService;

    @Test
    void greetUsesMockedRepositoryBean() {
        given(greetingRepository.findGreeting("World")).willReturn("Mocked greeting");

        assertThat(greetingService.greet("World")).isEqualTo("Mocked greeting");
    }
}
