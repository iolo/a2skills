.setcpu "6502"
.export start, done
.segment "CODE"
; Bare 6502 fixture, no DOS/runtime/zero-page dependency. 40-column page 1.
start:
    bit $C051                 ; text
    bit $C054                 ; page 1 (use main-memory 40-column profile)
    lda #$C1                  ; normal-video A
    sta $0400
    lda #$42                  ; observable completion marker
    sta $0300
done:
    jmp done                  ; safe with direct PC entry, no fabricated RTS
