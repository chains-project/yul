package com.example.model;

import lombok.NonNull;
import lombok.Value;

import java.math.BigDecimal;

/**
 * Immutable value example: {@code @Value} makes fields private final and
 * generates getters, an all-args constructor, {@code equals}/{@code hashCode}
 * and {@code toString}. For simple data carriers, a Java {@code record} is
 * also a good boilerplate-free option.
 */
@Value
public class Money {
    @NonNull BigDecimal amount;
    @NonNull String currency;
}
