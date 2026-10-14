package com.example.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Map;
import java.util.Properties;
import org.junit.jupiter.api.Test;

class DbConfigTest {

    @Test
    void systemPropertyOverridesEnvOverridesDefaults() {
        Properties defaults = new Properties();
        defaults.setProperty("db.url", "jdbc:mysql://default/db");
        defaults.setProperty("db.user", "defaultUser");
        defaults.setProperty("db.password", "defaultPass");

        Properties sysProps = new Properties();
        sysProps.setProperty("db.url", "jdbc:mysql://sysprop/db");

        DbConfig config = DbConfig.load(
                Map.of("DB_URL", "jdbc:mysql://env/db", "DB_USER", "envUser"), sysProps, defaults);

        assertEquals("jdbc:mysql://sysprop/db", config.url());
        assertEquals("envUser", config.user());
        assertEquals("defaultPass", config.password());
    }

    @Test
    void missingUrlFails() {
        assertThrows(IllegalStateException.class,
                () -> DbConfig.load(Map.of(), new Properties(), new Properties()));
    }

    @Test
    void toStringHidesPassword() {
        assertFalse(new DbConfig("u", "user", "secret").toString().contains("secret"));
    }
}
