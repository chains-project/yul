package com.example.api.greeting;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/greetings")
public class GreetingController {

    @GetMapping
    public Greeting greet(@RequestParam(defaultValue = "World") @NotBlank @Size(max = 50) String name) {
        return new Greeting("Hello, " + name + "!");
    }
}
