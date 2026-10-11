package com.example.restapi.service;

import com.example.restapi.exception.ResourceNotFoundException;
import com.example.restapi.model.Product;
import com.example.restapi.model.ProductRequest;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class ProductService {

    private final Map<Long, Product> products = new ConcurrentHashMap<>();
    private final AtomicLong sequence = new AtomicLong();

    public List<Product> findAll() {
        return new ArrayList<>(products.values());
    }

    public Product findById(Long id) {
        Product product = products.get(id);
        if (product == null) {
            throw new ResourceNotFoundException("Product not found with id " + id);
        }
        return product;
    }

    public Product create(ProductRequest request) {
        long id = sequence.incrementAndGet();
        Product product = new Product(id, request.name(), request.price());
        products.put(id, product);
        return product;
    }

    public Product update(Long id, ProductRequest request) {
        findById(id);
        Product product = new Product(id, request.name(), request.price());
        products.put(id, product);
        return product;
    }

    public void delete(Long id) {
        findById(id);
        products.remove(id);
    }
}
