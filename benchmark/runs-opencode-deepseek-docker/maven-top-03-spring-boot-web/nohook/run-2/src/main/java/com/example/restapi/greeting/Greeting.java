package com.example.restapi.greeting;

import jakarta.validation.constraints.NotBlank;

public record Greeting(Long id, @NotBlank String content) {
}
