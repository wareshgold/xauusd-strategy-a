# Step 3 Capture Mode Addendum

The Step 3 forward runner now supports:

`SP2L_FORENSIC_CAPTURE_ONLY=1`

In this mode the runner:

- continues using the real MT5 rolling acquisition path;
- records Step 3 DATA_SNAPSHOT / DETECTOR_RESULT / POLL_HEALTH telemetry;
- does not place demo orders;
- does not send order/lifecycle Telegram notifications;
- does not change the shared detector;
- does not alter SP2L geometry or execution semantics.

This isolates the forensic acquisition question from trading activity.

Recommended evidence run:

```powershell
$env:SP2L_FORENSIC_STEP3_TELEMETRY="1"
$env:SP2L_FORENSIC_CAPTURE_ONLY="1"
$env:FORWARD_TEST_SECONDS="1800"
```

Then run the existing forward runner and allow the 30-minute capture to complete.

The resulting JSONL event stream should be preserved as the Step 3 evidence artifact before any interpretation is made.
