package com.bebrample.backend.room.ws;

import com.bebrample.backend.common.exception.RoomException;
import com.bebrample.backend.room.RedisLockManager;
import com.bebrample.backend.room.RoomService;
import com.bebrample.backend.room.ws.dto.MessageDto;
import com.bebrample.backend.room.ws.dto.MoveDto;
import com.bebrample.backend.room.ws.dto.WebSocketEvent;
import com.bebrample.backend.user.entity.LobbyParticipant;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.web.server.ResponseStatusException;

import java.security.Principal;
import java.time.Duration;

@Slf4j
@Controller
@RequiredArgsConstructor
public class RoomWebSocketController {
    private final RoomService roomService;
    private final RedisLockManager redisLockManager;
    private final SimpMessagingTemplate simpMessagingTemplate;
    private final RoomWebSocketService roomWebSocketService;
    @MessageMapping("/rooms/{uuid}/move")
    public void makeMove(@DestinationVariable String uuid, MoveDto move, Principal principal) {

        String lockKey = "room:state:" + uuid;

        String lockId = redisLockManager.tryLock(lockKey, Duration.ofSeconds(5));
        if(lockId == null) throw new RoomException("Move was made while moves are locked.");
        LobbyParticipant user = checkAndReturnParticipant(principal);
        try {
            roomService.updateChessState(uuid, move, user);
            log.info("move was made");
        } finally {
            redisLockManager.unlockLock(lockKey, lockId);
        }
    }

    @MessageMapping("/rooms/{uuid}/message")
    public void handleMessage(@DestinationVariable String uuid, MessageDto message, Principal principal){
        LobbyParticipant user = checkAndReturnParticipant(principal);
        MessageDto messageToSend = roomWebSocketService.saveMessage(uuid, message, user);
        simpMessagingTemplate.convertAndSend("/topic/rooms/" + uuid, new WebSocketEvent<>("MESSAGE", messageToSend));
    }


    private LobbyParticipant checkAndReturnParticipant(Principal principal) {
        Authentication auth = (Authentication) principal;
        LobbyParticipant user = (LobbyParticipant) auth.getPrincipal();
        if (user == null) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "You are not authorized.");
        return user;
    }

}