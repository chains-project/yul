package com.example.inventory.service;

public class ProductNotFoundException extends RuntimeException {

    public ProductNotFoundException(Long id) {
        super("Product " + id + " not found");
    }

    public ProductNotFoundException(String sku) {
        super("Product with SKU " + sku + " not found");
    }
}
