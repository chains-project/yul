package com.example.product.service;

import com.example.product.domain.Product;
import com.example.product.repository.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Product> findAll() {
        return productRepository.findAll();
    }

    public Optional<Product> findById(Long id) {
        return productRepository.findById(id);
    }

    public List<Product> search(String name) {
        return productRepository.findByNameContainingIgnoreCase(name);
    }

    public List<Product> findExpensiveProducts(BigDecimal min) {
        return productRepository.findExpensiveProducts(min);
    }

    @Transactional
    public Product create(Product product) {
        return productRepository.save(product);
    }

    @Transactional
    public Optional<Product> update(Long id, Product updates) {
        return productRepository.findById(id)
                .map(existing -> {
                    existing.setName(updates.getName());
                    existing.setDescription(updates.getDescription());
                    existing.setPrice(updates.getPrice());
                    return existing;
                });
    }

    @Transactional
    public boolean delete(Long id) {
        if (!productRepository.existsById(id)) {
            return false;
        }
        productRepository.deleteById(id);
        return true;
    }
}
