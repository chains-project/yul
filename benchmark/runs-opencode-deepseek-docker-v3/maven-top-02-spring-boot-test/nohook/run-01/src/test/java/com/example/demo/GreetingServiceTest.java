package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

	@Mock
	private Clock clock;

	@Test
	void greetIncludesNameAndCurrentDate() {
		given(clock.getZone()).willReturn(ZoneOffset.UTC);
		given(clock.instant()).willReturn(Instant.parse("2026-10-03T12:00:00Z"));

		GreetingService service = new GreetingService(clock);

		assertThat(service.greet("Ada")).isEqualTo("Hello, Ada! Today is 2026-10-03.");
	}

}
