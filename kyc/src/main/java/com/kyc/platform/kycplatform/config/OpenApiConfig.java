package com.kyc.platform.kycplatform.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.*;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(apiInfo())
                .servers(List.of(
                        new Server().url("http://localhost:8080").description("Development Server"),
                        new Server().url("https://api.kycplatform.com").description("Production Server")
                ))
                .components(securityComponents());
    }

    private Info apiInfo() {
        return new Info()
                .title("KYC Platform API")
                .description("Autonomous Compliance Intelligence Platform - API Documentation")
                .version("1.0.0")
                .contact(new Contact()
                        .name("KYC Platform Team")
                        .email("support@kycplatform.com"))
                .license(new License()
                        .name("MIT License")
                        .url("https://opensource.org/licenses/MIT"));
    }

    private Components securityComponents() {
        SecurityScheme securityScheme = new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")
                .description("Enter JWT token");

        SecurityRequirement securityRequirement = new SecurityRequirement()
                .addList("Bearer Authentication");

        return new Components()
                .addSecuritySchemes("Bearer Authentication", securityScheme)
                .addSecurityItem(securityRequirement);
    }
}