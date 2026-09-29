package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/greetings")
public class GreetingController {

	@GetMapping("/{name}")
	public Greeting greet(@PathVariable String name) {
		return new Greeting("Hello, " + name + "!");
	}

	public record Greeting(String message) {
	}

}
