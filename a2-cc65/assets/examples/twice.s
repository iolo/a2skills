.export _twice
.segment "CODE"
; No memory or zero-page ownership. Clobbers A, X, and flags; preserves Y.
; Arithmetic wraps modulo 256.
_twice:
    asl a
    ldx #0
    rts
