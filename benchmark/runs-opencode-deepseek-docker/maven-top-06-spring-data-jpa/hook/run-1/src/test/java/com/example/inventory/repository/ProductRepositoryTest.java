package com.example.inventory.repository;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.example.inventory.domain.Product;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.dao.DataIntegrityViolationException;

@DataJpaTest
class ProductRepositoryTest {

    @Autowired
    private ProductRepository repository;

    @Test
    void savesAndLoadsProduct() {
        Product saved = repository.saveAndFlush(new Product("SKU-1", "Widget", new BigDecimal("9.99"), 5));

        assertThat(saved.getId()).isNotNull();
        assertThat(saved.getCreatedAt()).isNotNull();
        assertThat(saved.getUpdatedAt()).isNotNull();

        Optional<Product> found = repository.findBySku("SKU-1");
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Widget");
    }

    @Test
    void searchesByNameCaseInsensitively() {
        repository.save(new Product("SKU-2", "Blue Widget", new BigDecimal("1.00"), 1));
        repository.save(new Product("SKU-3", "Red Gadget", new BigDecimal("2.00"), 2));
        repository.save(new Product("SKU-4", "Blue Gadget", new BigDecimal("3.00"), 3));
        repository.flush();

        List<Product> matches = repository.findByNameContainingIgnoreCaseOrderByNameAsc("blue");

        assertThat(matches).extracting(Product::getSku).containsExactly("SKU-4", "SKU-2");
    }

    @Test
    void rejectsDuplicateSku() {
        repository.saveAndFlush(new Product("SKU-DUP", "First", new BigDecimal("1.00"), 1));

        assertThatThrownBy(() ->
                        repository.saveAndFlush(new Product("SKU-DUP", "Second", new BigDecimal("2.00"), 2)))
                .isInstanceOf(DataIntegrityViolationException.class);
    }

    @Test
    void reportsExistenceBySku() {
        repository.saveAndFlush(new Product("SKU-5", "Thing", new BigDecimal("4.00"), 4));

        assertThat(repository.existsBySku("SKU-5")).isTrue();
        assertThat(repository.existsBySku("SKU-UNKNOWN")).isFalse();
    }
}
