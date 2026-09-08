package com.bebrample.backend.room.ws;

import com.bebrample.backend.room.RedisRepository;
import com.bebrample.backend.room.ws.dto.MessageDto;
import com.bebrample.backend.user.entity.LobbyParticipant;
import jakarta.persistence.Lob;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RoomWebSocketService {
    private final RedisRepository redisRepository;

    public MessageDto saveMessage(String roomUuid, MessageDto message, LobbyParticipant user){
        MessageDto savedMessage = new MessageDto(message.getMessage(), user.getUsername());
        redisRepository.saveMessage(roomUuid, savedMessage);
        return savedMessage;
    }

    public List<MessageDto> getMessages(String roomUuid){
       return redisRepository.getMessages(roomUuid);
    }
}
