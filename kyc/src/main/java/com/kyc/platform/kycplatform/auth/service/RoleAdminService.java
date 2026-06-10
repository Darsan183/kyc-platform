package com.kyc.platform.kycplatform.auth.service;

import com.kyc.platform.kycplatform.auth.domain.Role;
import com.kyc.platform.kycplatform.auth.domain.User;
import com.kyc.platform.kycplatform.auth.dto.UserDto;
import com.kyc.platform.kycplatform.auth.repository.RoleRepository;
import com.kyc.platform.kycplatform.auth.repository.UserRepository;
import com.kyc.platform.kycplatform.shared.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Set;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Transactional
public class RoleAdminService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;

    public UserDto assignRole(UUID userId, Role.RoleName roleName) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        Role role = roleRepository.findByName(roleName)
                .orElseThrow(() -> new RuntimeException("Role not found: " + roleName));
        
        user.addRole(role);
        User savedUser = userRepository.save(user);
        return UserDto.fromEntity(savedUser);
    }

    public UserDto removeRole(UUID userId, Role.RoleName roleName) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        Role role = roleRepository.findByName(roleName)
                .orElseThrow(() -> new RuntimeException("Role not found: " + roleName));
        
        user.removeRole(role);
        User savedUser = userRepository.save(user);
        return UserDto.fromEntity(savedUser);
    }

    @Transactional(readOnly = true)
    public Page<UserDto> getUsersByRole(Role.RoleName roleName, Pageable pageable) {
        return userRepository.findAll(pageable)
                .map(UserDto::fromEntity);
    }
}