package com.example.inventory.web;

import com.example.inventory.domain.Product;
import java.math.BigDecimal;
import java.time.Instant;

public record ProductResponse(
        Long id,
        String sku,
        String name,
        BigDecimal price,
        int quantity,
        long version,
        Instant createdAt,
        Instant updatedAt) {

    public static ProductResponse from(Product product) {
        return new ProductResponse(
                product.getId(),
                product.getSku(),
                product.getName(),
                product.getPrice(),
                product.getQuantity(),
                product.getVersion(),
                product.getCreatedAt(),
                product.getUpdatedAt());
    }
}
