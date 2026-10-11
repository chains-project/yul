package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private MessageProvider messageProvider;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void greetUsesMessageFromProvider() {
        given(messageProvider.getMessage()).willReturn("Hi");

        String greeting = greetingService.greet("World");

        assertThat(greeting).isEqualTo("Hi, World!");
        verify(messageProvider).getMessage();
    }
}
