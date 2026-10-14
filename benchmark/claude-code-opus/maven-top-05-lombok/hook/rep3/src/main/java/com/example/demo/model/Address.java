package com.example.demo.model;

import lombok.Value;

/**
 * Immutable value object: {@code @Value} makes fields private final and generates
 * getters, an all-args constructor, {@code equals}/{@code hashCode} and {@code toString}.
 */
@Value
public class Address {
    String street;
    String city;
    String postalCode;
}
