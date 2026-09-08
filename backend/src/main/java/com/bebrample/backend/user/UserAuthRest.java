package com.bebrample.backend.user;

import com.bebrample.backend.common.security.CookieService;
import com.bebrample.backend.user.dto.UserCreateDto;
import com.bebrample.backend.user.dto.UserResponseDto;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@Validated
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class UserAuthRest {

    private final UserService userService;
    private final CookieService cookieService;

    @PostMapping("/register")
    public UserResponseDto createAccount(@Valid @RequestBody UserCreateDto dto){
        return userService.register(dto);
    }

    @PostMapping("/login")
    public ResponseEntity<UserResponseDto> loginToAccount(@Valid @RequestBody UserCreateDto dto, HttpServletResponse response){
        String jwt = userService.login(dto);
        ResponseCookie cookie = cookieService.createCookie(jwt);
        response.setHeader(HttpHeaders.SET_COOKIE, cookie.toString());
        UserResponseDto user = userService.findByName(dto.getUsername());
        return ResponseEntity.ok(user);

    }

    @PostMapping("/logout")
    public ResponseEntity<String> logoutFromAccount(HttpServletResponse response){
        ResponseCookie cookie = cookieService.deleteCookie();
        response.setHeader(HttpHeaders.SET_COOKIE, cookie.toString());
        return ResponseEntity.ok("logged out");
    }

    @PostMapping("/anonymous")
    @Operation(summary = "Create guest session")
    public ResponseEntity<String> createAnonymousAccount(HttpServletResponse response){
        String jwt = userService.createGuest();
        ResponseCookie cookie = cookieService.createCookie(jwt);
        response.setHeader(HttpHeaders.SET_COOKIE, cookie.toString());
        return ResponseEntity.ok("created anonymous account");
    }
}
