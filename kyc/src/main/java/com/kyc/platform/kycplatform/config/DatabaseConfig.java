package com.kyc.platform.kycplatform.config;

import org.hibernate.boot.model.naming.PhysicalNamingStrategy;
import org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl;
import org.hibernate.engine.jdbc.env.spi.JdbcEnvironment;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

import java.io.Serializable;
import java.util.Locale;

@Configuration
@EnableJpaRepositories(
    basePackages = "com.kyc.platform.kycplatform.infrastructure.repository",
    repositoryImplementationPostfix = "Impl"
)
@EnableConfigurationProperties(HibernateProperties.class)
public class DatabaseConfig {

    @Bean
    public PhysicalNamingStrategy physicalNamingStrategy() {
        return new PhysicalNamingStrategy() {
            @Override
            public String toPhysicalCatalogName(Serializable catalog, JdbcEnvironment context) {
                return catalog != null ? catalog.toString() : null;
            }

            @Override
            public String toPhysicalSchemaName(Serializable schema, JdbcEnvironment context) {
                return schema != null ? schema.toString() : null;
            }

            @Override
            public String toPhysicalTableName(String name, JdbcEnvironment context) {
                return name.toLowerCase(Locale.ROOT);
            }

            @Override
            public String toPhysicalSequenceName(String name, JdbcEnvironment context) {
                return name.toLowerCase(Locale.ROOT);
            }

            @Override
            public String toPhysicalColumnName(String name, JdbcEnvironment context) {
                return name.toLowerCase(Locale.ROOT);
            }
        };
    }
}