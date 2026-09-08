package com.bebrample.backend.chess;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class MakeMoveRequestDto {
    // i hope
    private String fen;
    private String move;
}
