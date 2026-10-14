package com.example.api.item;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ItemRequest(
        @NotBlank @Size(max = 100) String name,
        @Size(max = 500) String description) {
}
