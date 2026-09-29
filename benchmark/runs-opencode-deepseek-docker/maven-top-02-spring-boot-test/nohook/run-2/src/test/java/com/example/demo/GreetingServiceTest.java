package com.example.demo;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private MessageRepository messageRepository;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void greetBuildsMessageFromRepositoryTemplate() {
        given(messageRepository.findTemplate()).willReturn("Hi");

        String result = greetingService.greet("Alice");

        assertThat(result).isEqualTo("Hi, Alice!");
        verify(messageRepository).findTemplate();
    }
}
