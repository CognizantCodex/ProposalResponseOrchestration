# RFP Status Tracker

`RFP_Status_Tracker.xlsx` is the intake ledger written by ReceiverAgent. The first validated file is registered by SHA-256 and its metadata row is retained. A replay with the same SHA-256 is rejected as a duplicate and does not append another row.

The workbook template is committed at the repository root; runtime executions use `RFP_TRACKER_PATH` (default `data/RFP_Status_Tracker.xlsx`).
