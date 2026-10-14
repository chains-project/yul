package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

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
    private GreetingService greetingService;

    @Test
    void greetsUsingTemplateFromRepository() {
        when(repository.findTemplate()).thenReturn("Hey %s");

        assertThat(greetingService.greet("Ada")).isEqualTo("Hey Ada");
        verify(repository).findTemplate();
    }
}
