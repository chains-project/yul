package com.example.model;

import lombok.Value;

/** Immutable example: {@code @Value} makes fields private final and generates an all-args constructor and getters. */
@Value
public class Address {
    String street;
    String city;
}
