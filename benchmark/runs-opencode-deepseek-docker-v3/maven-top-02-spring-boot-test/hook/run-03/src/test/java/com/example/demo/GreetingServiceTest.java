package com.example.demo;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class GreetingServiceTest {

	@Mock
	private GreetingRepository greetingRepository;

	@InjectMocks
	private GreetingService greetingService;

	@Test
	void greetCombinesRepositoryGreetingWithName() {
		given(this.greetingRepository.findGreeting()).willReturn("Hi");

		assertThat(this.greetingService.greet("Ada")).isEqualTo("Hi, Ada!");
		verify(this.greetingRepository).findGreeting();
	}

}
