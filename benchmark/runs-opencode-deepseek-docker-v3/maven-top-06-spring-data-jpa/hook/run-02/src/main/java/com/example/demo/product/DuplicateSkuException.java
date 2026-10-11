package com.example.demo.product;

public class DuplicateSkuException extends RuntimeException {

    public DuplicateSkuException(String sku) {
        super("Product with sku already exists: " + sku);
    }
}
