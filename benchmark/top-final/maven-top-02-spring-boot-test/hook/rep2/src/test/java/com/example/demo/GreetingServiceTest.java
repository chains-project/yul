package com.example.demo;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private GreetingRepository greetingRepository;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void greetReturnsMessageBuiltFromRepositoryName() {
        when(greetingRepository.findNameById(1L)).thenReturn("Ada");

        String result = greetingService.greet(1L);

        assertThat(result).isEqualTo("Hello, Ada!");
        verify(greetingRepository).findNameById(1L);
    }

}
