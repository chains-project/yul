package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@SpringBootTest
class GreetingServiceTests {

    @Autowired
    private GreetingService greetingService;

    @MockitoBean
    private GreetingRepository greetingRepository;

    @Test
    void greetAppendsWorldToRepositoryGreeting() {
        when(greetingRepository.findGreeting()).thenReturn("Hi");

        String result = greetingService.greet();

        assertThat(result).isEqualTo("Hi, World!");
        verify(greetingRepository).findGreeting();
    }

}
