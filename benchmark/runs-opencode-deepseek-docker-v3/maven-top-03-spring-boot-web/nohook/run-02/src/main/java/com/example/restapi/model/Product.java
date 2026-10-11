package com.example.restapi.model;

import java.math.BigDecimal;

public record Product(Long id, String name, BigDecimal price) {
}
