package com.example.demo.greeting;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

/**
 * Plain unit test: Mockito for mocking, AssertJ for assertions.
 */
@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private GreetingRepository repository;

    @InjectMocks
    private GreetingService service;

    @Test
    void greetsWithNameResolvedFromRepository() {
        given(this.repository.findName(1L)).willReturn("World");

        String greeting = this.service.greet(1L);

        assertThat(greeting).isEqualTo("Hello, World!");
        verify(this.repository).findName(1L);
    }

}
