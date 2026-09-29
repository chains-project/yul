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
    private GreetingRepository repository;

    @InjectMocks
    private GreetingService service;

    @Test
    void greetUsesNameFromRepository() {
        given(repository.findName(1L)).willReturn("World");

        String result = service.greet(1L);

        assertThat(result).isEqualTo("Hello, World!");
        verify(repository).findName(1L);
    }
}
