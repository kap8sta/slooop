package com.bebrample.backend.room.ws;

import com.bebrample.backend.common.exception.ResourcesNotFoundException;
import com.bebrample.backend.entity.Role;
import com.bebrample.backend.room.RedisRepository;
import com.bebrample.backend.room.Room;
import com.bebrample.backend.room.ws.dto.ConnectDto;
import com.bebrample.backend.room.ws.dto.MoveDto;
import com.bebrample.backend.room.ws.dto.WebSocketEvent;
import com.bebrample.backend.user.entity.LobbyParticipant;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.http.HttpStatus;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.socket.messaging.SessionDisconnectEvent;
import org.springframework.web.socket.messaging.SessionSubscribeEvent;

import java.security.Principal;
import java.util.List;
import java.util.Objects;

@Component
@Slf4j
@RequiredArgsConstructor
public class RoomWebSocketListener {
    private final SimpMessagingTemplate simpMessagingTemplate;
    private final RedisRepository redisRepository;
    private final RoomWebSocketService roomWebSocketService;
    private static final String destinationPrefix = "/topic/rooms/";
    @EventListener
    public void onConnect(SessionSubscribeEvent event){
        StompHeaderAccessor accessor = StompHeaderAccessor.wrap(event.getMessage());
        String destination = accessor.getDestination();
        var sessionAttributes = accessor.getSessionAttributes();
        String roomUuid;
        if (destination != null && sessionAttributes != null) {
            sessionAttributes.put("destination", destination);
            roomUuid = destination.substring(destinationPrefix.length());

        } else {
            log.info("cant get destination");
            throw new ResourcesNotFoundException("cant get destination");
        }
        LobbyParticipant participant = checkAndReturnLobbyParticipant(accessor);
        Room room = redisRepository.getRoom(roomUuid);

        if(room == null) throw new ResourcesNotFoundException("this Room isn't accessible anymore");
        boolean isPlayer = Objects.equals(room.getFirstPlayer().getId(), participant.getId())
                || (room.getSecondPlayer() != null
                && Objects.equals(room.getSecondPlayer().getId(), participant.getId()));
        if(isPlayer) redisRepository.saveOrUpdateUser(roomUuid, participant.getId());

        List<MoveDto> moves = redisRepository.getMoves(roomUuid);
        ConnectDto dto = getConnectDto(participant, room);
        simpMessagingTemplate.convertAndSend(destination, new WebSocketEvent<>("CONNECTED", dto));
        simpMessagingTemplate.convertAndSend(destination, new WebSocketEvent<>("ROOM_INFO", room));
        simpMessagingTemplate.convertAndSend(destination, new WebSocketEvent<>("MATCH_MOVES", moves));
        roomWebSocketService.getMessages(roomUuid)
                .forEach(message ->
                        simpMessagingTemplate
                                .convertAndSend(destination, new WebSocketEvent<>("MESSAGE", message)));
    }

    @EventListener
    public void onDisconnect(SessionDisconnectEvent event){
        StompHeaderAccessor accessor = StompHeaderAccessor.wrap(event.getMessage());

        var sessionAttributes = accessor.getSessionAttributes();

        if (sessionAttributes != null) {
            String destination = (String) sessionAttributes.get("destination");
            String roomUuid = destination.substring(destinationPrefix.length());


            LobbyParticipant participant = checkAndReturnLobbyParticipant(accessor);
            Room room = redisRepository.getRoom(roomUuid);
            redisRepository.deleteUser(participant.getId());
            if(room == null) throw new ResourcesNotFoundException("this Room isn't accessible anymore");
            ConnectDto dto = getConnectDto(participant, room);
            simpMessagingTemplate.convertAndSend(destination, new WebSocketEvent<>("DISCONNECTED", dto));
        }
    }

    private ConnectDto getConnectDto(LobbyParticipant participant, Room room) {
        ConnectDto dto = new ConnectDto();
        dto.setPlayerName(participant.getUsername());
        String redisRoomUuid = redisRepository.getUserRoomUuid(participant.getId());
        if(redisRoomUuid != null) {
            if (redisRoomUuid.equals(room.getUuid())) dto.setRole(Role.PLAYER);
        }
        else dto.setRole(Role.SPECTATOR);
        dto.setRoomState(room.getRoomState());
        return dto;
    }

    private static LobbyParticipant checkAndReturnLobbyParticipant(StompHeaderAccessor accessor) {
        Principal principal = accessor.getUser();
        UsernamePasswordAuthenticationToken auth = (UsernamePasswordAuthenticationToken) principal;
        if(auth == null) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "You are not authorized.");
        return (LobbyParticipant) auth.getPrincipal();
    }
}
