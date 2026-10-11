package com.example.demo.product;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ProductRepository extends JpaRepository<Product, Long> {

    Optional<Product> findBySku(String sku);

    boolean existsBySku(String sku);

    List<Product> findByNameContainingIgnoreCase(String name);

    @Query("select p from Product p where p.price between :min and :max order by p.price")
    List<Product> findByPriceRange(@Param("min") java.math.BigDecimal min,
            @Param("max") java.math.BigDecimal max);
}
