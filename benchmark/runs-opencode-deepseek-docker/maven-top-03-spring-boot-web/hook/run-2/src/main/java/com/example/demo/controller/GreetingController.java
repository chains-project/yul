package com.example.demo.controller;

import jakarta.validation.constraints.NotBlank;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class GreetingController {

    @GetMapping("/hello")
    public Map<String, Object> hello(@RequestParam(defaultValue = "World") String name) {
        return Map.of(
                "message", "Hello, " + name + "!",
                "timestamp", Instant.now().toString()
        );
    }

    @GetMapping("/greetings/{name}")
    public ResponseEntity<Map<String, Object>> greeting(@PathVariable String name) {
        return ResponseEntity.ok(Map.of(
                "message", "Hello, " + name + "!",
                "timestamp", Instant.now().toString()
        ));
    }

    @PostMapping("/greetings")
    public ResponseEntity<Map<String, Object>> createGreeting(@RequestBody GreetingRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "greeting", "Hello, " + request.name() + "!",
                "timestamp", Instant.now().toString()
        ));
    }

    public record GreetingRequest(@NotBlank String name) {
    }
}
