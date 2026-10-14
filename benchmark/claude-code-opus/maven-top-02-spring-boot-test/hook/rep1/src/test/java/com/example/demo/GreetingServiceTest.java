package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

/** Plain unit test: no Spring context, just Mockito. */
@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private GreetingRepository repository;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void formatsTemplateWithName() {
        when(repository.findTemplate()).thenReturn("Hey %s");

        assertThat(greetingService.greet("Alice")).isEqualTo("Hey Alice");
        verify(repository).findTemplate();
    }
}
