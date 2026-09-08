package com.bebrample.backend.common.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.bebrample.backend.user.entity.Guest;
import com.bebrample.backend.user.entity.LobbyParticipant;
import com.bebrample.backend.user.entity.User;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;

import java.io.IOException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class JwtFilter extends OncePerRequestFilter {

    private final JwtService jwtService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
                                    throws ServletException, IOException {
        Cookie[] cookies = request.getCookies();
        String token = null;

        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if ("access_token".equals(cookie.getName())) {
                    token = cookie.getValue();
                }
            }
            if (token != null && jwtService.verifyToken(token)) {

                DecodedJWT decodedJWT = JWT.decode(token);
                String idStr = decodedJWT.getSubject();
                Long id = Long.parseLong(idStr);
                String username = decodedJWT.getClaim("username").asString();
                String role = decodedJWT.getClaim("role").asString();


                LobbyParticipant participant;
                if(role.equals("ROLE_GUEST")) participant = new Guest(id, username);
                else participant = User.builder().id(id).username(username).build();

                List<GrantedAuthority> authorities = AuthorityUtils.createAuthorityList(role);

                UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                        participant, null, authorities);

                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        }
        filterChain.doFilter(request, response);
    }
}
