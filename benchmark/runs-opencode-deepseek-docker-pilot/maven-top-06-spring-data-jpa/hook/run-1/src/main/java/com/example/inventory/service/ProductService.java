package com.example.inventory.service;

import com.example.inventory.domain.Product;
import com.example.inventory.repository.ProductRepository;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class ProductService {

    private final ProductRepository repository;

    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public List<Product> findAll() {
        return repository.findAll();
    }

    public List<Product> searchByName(String name) {
        if (name == null || name.isBlank()) {
            return repository.findAll();
        }
        return repository.findByNameContainingIgnoreCaseOrderByNameAsc(name);
    }

    public Product findById(Long id) {
        return repository.findById(id).orElseThrow(() -> new ProductNotFoundException(id));
    }

    public Product findBySku(String sku) {
        return repository
                .findBySku(sku)
                .orElseThrow(() -> new ProductNotFoundException(sku));
    }

    @Transactional
    public Product create(Product product) {
        if (repository.existsBySku(product.getSku())) {
            throw new IllegalArgumentException("SKU already exists: " + product.getSku());
        }
        return repository.save(product);
    }

    @Transactional
    public Product update(Long id, Product changes) {
        Product product = findById(id);
        product.setName(changes.getName());
        product.setPrice(changes.getPrice());
        product.setQuantity(changes.getQuantity());
        return repository.save(product);
    }

    @Transactional
    public void delete(Long id) {
        if (!repository.existsById(id)) {
            throw new ProductNotFoundException(id);
        }
        repository.deleteById(id);
    }
}
