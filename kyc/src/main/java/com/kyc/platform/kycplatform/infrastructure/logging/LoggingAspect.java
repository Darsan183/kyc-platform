package com.kyc.platform.kycplatform.infrastructure.logging;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Aspect
@Component
@Slf4j
public class LoggingAspect {

    @Around("@within(org.springframework.stereotype.Controller)")
    public Object logController(ProceedingJoinPoint joinPoint) throws Throwable {
        String traceId = UUID.randomUUID().toString();
        MDC.put("traceId", traceId);
        
        long startTime = System.currentTimeMillis();
        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        
        log.info("Entering {}.{} with args: {}", className, methodName, joinPoint.getArgs());
        
        try {
            Object result = joinPoint.proceed();
            long duration = System.currentTimeMillis() - startTime;
            log.info("Exiting {}.{} with result: {} in {}ms", className, methodName, result, duration);
            return result;
        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            log.error("Exception in {}.{} after {}ms: {}", className, methodName, duration, e.getMessage(), e);
            throw e;
        } finally {
            MDC.remove("traceId");
        }
    }
}