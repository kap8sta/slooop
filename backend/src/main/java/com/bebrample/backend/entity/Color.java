package com.bebrample.backend.entity;

public enum Color {
    WHITE,
    BLACK;
    public Color toggle() {
        return this == WHITE ? BLACK : WHITE;
    }
}
