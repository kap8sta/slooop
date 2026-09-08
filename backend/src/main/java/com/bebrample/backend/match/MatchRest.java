package com.bebrample.backend.match;

import com.bebrample.backend.match.dto.MatchResponseDto;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/")
public class MatchRest {
    private final MatchService matchService;

    @GetMapping("player/matches/{id}")
    @Operation(summary = "Get player matches by player id")
    public List<MatchResponseDto> getPlayerMatches(@PathVariable Long id){
        return matchService.getPlayerMatches(id);
    }
    @GetMapping("matches/{id}")
    @Operation(summary = "Get match by match id")
    public MatchResponseDto getMatch(@PathVariable Long id){
        return matchService.getMatch(id);
    }

    @GetMapping("matches")
    @Operation(summary = "Get all avaiable matches")
    public List<MatchResponseDto> getAllMatches(){
        return matchService.getAllMatches();
    }
}
