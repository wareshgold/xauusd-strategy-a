# SP2L F10 Stop Source Resolution — 2026-09-21

## Confirmed source meaning
The preserved source supports placing the stop behind the candle from which the spike originated and shows stop distance considered before activation.

## Unresolved
- wick extreme vs body field
- exact spike-origin candle mapping
- buffer amount, if any
- invalidation by touch, breach, or close
- replacement semantics when stop distance changes

## Gate
**PASS — source meaning is preserved; exact executable stop semantics remain unresolved.**

No canonical or production logic changed.