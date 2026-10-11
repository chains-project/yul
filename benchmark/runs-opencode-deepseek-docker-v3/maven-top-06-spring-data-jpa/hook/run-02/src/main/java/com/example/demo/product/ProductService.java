package com.example.demo.product;

import java.math.BigDecimal;
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

    @Transactional
    public Product create(String name, String sku, BigDecimal price) {
        if (repository.existsBySku(sku)) {
            throw new DuplicateSkuException(sku);
        }
        return repository.save(new Product(name, sku, price));
    }

    public Product findById(Long id) {
        return repository.findById(id).orElseThrow(() -> new ProductNotFoundException(id));
    }

    public List<Product> findAll() {
        return repository.findAll();
    }

    @Transactional
    public Product update(Long id, String name, BigDecimal price) {
        Product product = findById(id);
        product.setName(name);
        product.setPrice(price);
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
