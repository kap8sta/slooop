package com.bebrample.backend.room;

import com.bebrample.backend.user.entity.LobbyParticipant;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rooms")
@RequiredArgsConstructor
public class RoomRest {
    private final RoomService roomService;

    @PostMapping
    @Operation(summary = "Create room")
    public Room createGame(){
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        LobbyParticipant participant = (LobbyParticipant) auth.getPrincipal();
            return roomService.createRoom(participant);
    }

    @PostMapping("{uuid}")
    @Operation(summary = "Connect to room")
    public Room connectToRoom(@PathVariable String uuid){
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        LobbyParticipant participant = (LobbyParticipant) auth.getPrincipal();
        return roomService.connectToRoom(uuid, participant);
    }
    @GetMapping("/all-rooms")
    @Operation(summary = "Get all in-memory rooms")
    public List<Room> getAllRooms(){
        return roomService.findAllRooms();
    }

    @GetMapping("/all-playing-user")
    @Operation(summary = "Get all in-memory users who are playing")
    public List<String> getAllPlayingUsers(){
        return roomService.findAllPlayingUsers();
    }
}
