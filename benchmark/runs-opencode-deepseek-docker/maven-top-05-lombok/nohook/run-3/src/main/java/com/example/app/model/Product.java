package com.example.app.model;

import java.math.BigDecimal;

import lombok.Builder;
import lombok.Value;
import lombok.With;

/**
 * Immutable DTO.
 *
 * @Value makes all fields private final, generates getters, equals, hashCode,
 * toString and an all-args constructor (no setters).
 * @With generates "wither" copy methods for safe updates.
 */
@Value
@Builder
@With
public class Product {

    String sku;
    String name;
    BigDecimal price;
    int quantity;
}
