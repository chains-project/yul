package com.example.app.model;

import java.math.BigDecimal;

/**
 * Immutable value type. Prefer plain Java records for simple immutable data;
 * they need no Lombok at all.
 */
public record Money(BigDecimal amount, String currency) {
}
