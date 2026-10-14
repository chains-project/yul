package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

/** Plain unit test with Mockito, no Spring context. */
@ExtendWith(MockitoExtension.class)
class GreetingServiceTests {

    @Mock
    private GreetingRepository repository;

    @InjectMocks
    private GreetingService service;

    @Test
    void greetFormatsTemplateFromRepository() {
        given(repository.findTemplate()).willReturn("Hi, %s.");

        assertThat(service.greet("Ada")).isEqualTo("Hi, Ada.");
        verify(repository).findTemplate();
    }
}
