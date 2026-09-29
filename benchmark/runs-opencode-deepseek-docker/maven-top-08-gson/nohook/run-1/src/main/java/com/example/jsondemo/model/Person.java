package com.example.jsondemo.model;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

public record Person(
        @JsonProperty("name") String name,
        @JsonProperty("age") int age,
        @JsonProperty("email") String email,
        @JsonProperty("roles") List<String> roles) {
}
