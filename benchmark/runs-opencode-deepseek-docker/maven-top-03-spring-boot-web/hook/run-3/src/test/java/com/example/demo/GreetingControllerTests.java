package com.example.demo;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

class GreetingControllerTests {

	private MockMvc mockMvc;

	@BeforeEach
	void setUp() {
		mockMvc = MockMvcBuilders.standaloneSetup(new GreetingController()).build();
	}

	@Test
	void greetReturnsGreeting() throws Exception {
		mockMvc.perform(get("/api/greetings/World"))
				.andExpect(status().isOk())
				.andExpect(content().json("{\"message\":\"Hello, World!\"}"));
	}

}
