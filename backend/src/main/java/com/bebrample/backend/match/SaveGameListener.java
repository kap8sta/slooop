package com.bebrample.backend.match;

import lombok.RequiredArgsConstructor;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class SaveGameListener {
    private final MatchService matchService;
    @Async
    @EventListener
    public void handleSaveGame(SaveMatchEvent event){
        matchService.saveMatch(event.getRoom(), event.getMoves(), event.getWinner(), event.getState());
    }
}
