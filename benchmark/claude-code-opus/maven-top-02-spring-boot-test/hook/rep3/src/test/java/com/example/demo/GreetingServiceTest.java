package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

/** Plain unit test with Mockito - no Spring context. */
@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private GreetingRepository repository;

    @InjectMocks
    private GreetingService service;

    @Test
    void greetFormatsTemplateFromRepository() {
        when(repository.findTemplate()).thenReturn("Hi, %s");

        assertThat(service.greet("Alice")).isEqualTo("Hi, Alice");
        verify(repository).findTemplate();
    }
}
