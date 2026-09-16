package com.example.demo;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class DemoServiceTest {

    @InjectMocks
    private DemoService demoService;

    @Test
    void testGetMessage_withMockitoAndAssertJ() {
        assertThat(demoService).isNotNull();

        String message = demoService.getMessage();
        assertThat(message).isEqualTo("Hello, World!");
    }
}