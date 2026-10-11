package com.example.demo;

import java.time.Clock;
import java.time.LocalDate;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

	private final Clock clock;

	public GreetingService(Clock clock) {
		this.clock = clock;
	}

	public String greet(String name) {
		return "Hello, %s! Today is %s.".formatted(name, LocalDate.now(clock));
	}

}
