package com.bebrample.backend.room.ws.config;

import com.auth0.jwt.JWT;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.bebrample.backend.common.security.JwtService;
import com.bebrample.backend.user.entity.Guest;
import com.bebrample.backend.user.entity.LobbyParticipant;
import com.bebrample.backend.user.entity.User;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.messaging.support.ChannelInterceptor;
import org.springframework.messaging.support.MessageHeaderAccessor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.AuthorityUtils;

import java.util.List;
import java.util.Objects;

@Slf4j
@RequiredArgsConstructor
public class StompAuthChannelInterceptor implements ChannelInterceptor {

    private final JwtService jwtService;


    @Override
    public Message<?> preSend(Message<?> message, MessageChannel messageChannel) {

        StompHeaderAccessor accessor = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);
        // TODO: check for blank websocket connections
        if (accessor != null && Objects.equals(StompCommand.CONNECT, accessor.getCommand())) {
            String token = (String) accessor.getSessionAttributes().get("jwt");

            if (token != null && jwtService.verifyToken(token)) {

                DecodedJWT decodedJWT = JWT.decode(token);
                String idStr = decodedJWT.getSubject();
                Long id = Long.parseLong(idStr);
                String username = decodedJWT.getClaim("username").asString();
                String role = decodedJWT.getClaim("role").asString();


                LobbyParticipant participant;
                if (role.equals("ROLE_GUEST")) participant = new Guest(id, username);
                else participant = User.builder().id(id).username(username).build();

                List<GrantedAuthority> authorities = AuthorityUtils.createAuthorityList(role);

                UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                        participant, null, authorities);

                accessor.setUser(auth);
            } else log.info("can't parse cookie..><");
        }

        return message;
    }
}
