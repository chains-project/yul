package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.then;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private GreetingRepository greetingRepository;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void greetReturnsGreetingFromRepository() {
        given(greetingRepository.findGreeting("World")).willReturn("Hello, World!");

        String result = greetingService.greet("World");

        assertThat(result).isEqualTo("Hello, World!");
        then(greetingRepository).should().findGreeting("World");
    }

    @Test
    void greetRejectsBlankName() {
        assertThatThrownBy(() -> greetingService.greet("  "))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("name must not be blank");

        then(greetingRepository).shouldHaveNoInteractions();
    }
}
