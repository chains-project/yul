package com.example.demo;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatIllegalArgumentException;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

    @Mock
    private PrefixProvider prefixProvider;

    @InjectMocks
    private GreetingService greetingService;

    @Test
    void greetsWithTheConfiguredPrefix() {
        given(prefixProvider.prefix()).willReturn("Bonjour");

        String greeting = greetingService.greet("Ada");

        assertThat(greeting).isEqualTo("Bonjour, Ada!");
        verify(prefixProvider).prefix();
    }

    @Test
    void rejectsBlankNames() {
        assertThatIllegalArgumentException()
                .isThrownBy(() -> greetingService.greet("  "))
                .withMessage("name must not be blank");
    }
}
