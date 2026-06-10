package com.kyc.platform.kycplatform.application;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import java.util.List;

public record PaginatedResponse<T>(
        List<T> content,
        int page,
        int size,
        long totalElements,
        int totalPages,
        boolean hasNext,
        boolean hasPrevious
) {
    public static <T> PaginatedResponse<T> of(List<T> content, Pageable pageable, long totalElements) {
        int totalPages = (int) Math.ceil((double) totalElements / pageable.getPageSize());
        return new PaginatedResponse<>(
                content,
                pageable.getPageNumber(),
                pageable.getPageSize(),
                totalElements,
                totalPages,
                pageable.getPageNumber() < totalPages - 1,
                pageable.getPageNumber() > 0
        );
    }

    public static <T> PaginatedResponse<T> empty(Pageable pageable) {
        return new PaginatedResponse<>(
                List.of(),
                pageable.getPageNumber(),
                pageable.getPageSize(),
                0,
                0,
                false,
                false
        );
    }

    public static <T> PaginatedResponse<T> from(Page<T> page) {
        return new PaginatedResponse<>(
                page.getContent(),
                page.getPageNumber(),
                page.getSize(),
                page.getTotalElements(),
                page.getTotalPages(),
                page.hasNext(),
                page.hasPrevious()
        );
    }
}