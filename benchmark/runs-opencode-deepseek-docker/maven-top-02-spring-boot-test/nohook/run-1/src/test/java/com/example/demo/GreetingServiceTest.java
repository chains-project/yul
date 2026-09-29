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
    private NameRepository nameRepository;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void greetUsesNameFromRepository() {
        given(nameRepository.findName(1L)).willReturn("Alice");

        String greeting = greetingService.greet(1L);

        assertThat(greeting).isEqualTo("Hello, Alice!");
        verify(nameRepository).findName(1L);
    }

}
