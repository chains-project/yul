package com.example.restapi.greeting;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record GreetingRequest(
        @NotBlank(message = "name must not be blank")
        @Size(max = 100, message = "name must be at most 100 characters")
        String name) {
}
