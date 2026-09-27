package com.example.restapi.greeting;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/greetings")
public class GreetingController {

	private static final String TEMPLATE = "Hello, %s!";

	@GetMapping("/{name}")
	public Greeting greet(@PathVariable String name) {
		return new Greeting(1L, TEMPLATE.formatted(name));
	}

}
