package com.example.api.hello;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/hello")
public class HelloController {

    @GetMapping
    public Greeting hello(@RequestParam(defaultValue = "World") @NotBlank @Size(max = 100) String name) {
        return new Greeting("Hello, " + name + "!");
    }
}
