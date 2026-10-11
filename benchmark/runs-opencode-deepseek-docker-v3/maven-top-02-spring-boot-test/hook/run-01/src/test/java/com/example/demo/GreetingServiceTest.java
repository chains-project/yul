package com.example.demo;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private GreetingRepository greetingRepository;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void greetReturnsGreetingFromRepository() {
        when(greetingRepository.findGreeting("Alice")).thenReturn("Hi, Alice!");

        String result = greetingService.greet("Alice");

        assertThat(result).isEqualTo("Hi, Alice!");
        verify(greetingRepository).findGreeting("Alice");
    }

    @Test
    void greetRejectsBlankName() {
        assertThatThrownBy(() -> greetingService.greet("  "))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("name");

        verifyNoInteractions(greetingRepository);
    }

    @Test
    void greetUsesAnyArgumentMatching() {
        when(greetingRepository.findGreeting(anyString())).thenReturn("Hey!");

        assertThat(greetingService.greet("Bob")).isEqualTo("Hey!");
    }
}
