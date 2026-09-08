package com.bebrample.backend.user;

import com.bebrample.backend.user.dto.UserResponseDto;
import com.bebrample.backend.user.entity.LobbyParticipant;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.security.Principal;
import java.time.Instant;
import java.util.List;

@RequiredArgsConstructor
@RestController
@RequestMapping("/api/user")
public class UserRest {

    private final UserService userService;

    @GetMapping("/{id}")
    @Operation(summary = "Get user by id")
    public UserResponseDto getUser(@PathVariable Long id){
        return userService.findById(id);
    }

    @GetMapping()
    @Operation(summary = "Get all users")
    public List<UserResponseDto> getAllUsers(){
        return userService.findAll();
    }

    @GetMapping("/me")
    @Operation(summary = "returns info about currently logged in user")
    public UserResponseDto getMe(Principal principal){
        Authentication auth = (Authentication) principal;
        LobbyParticipant user = (LobbyParticipant) auth.getPrincipal();
        if (user.isGuest()) {
            return new UserResponseDto(user.getId(), user.getUsername(), Instant.EPOCH);
        }
        return userService.findById(user.getId());
    }
}
