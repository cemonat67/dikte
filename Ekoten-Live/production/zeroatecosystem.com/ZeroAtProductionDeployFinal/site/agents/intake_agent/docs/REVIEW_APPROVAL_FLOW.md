# Review & Approval Flow

## Statuses
- draft
- extracted
- normalized
- in_review
- approved
- rejected
- archived

## Review checklist
- source identity confirmed
- facility confirmed
- period confirmed
- unit normalization checked
- duplicate record check passed
- low-confidence fields manually verified
- financial overlay optional but flagged if missing

## Approval rules
Approved only if:
- required fields exist
- confidence score >= threshold or manually overridden
- reviewer name entered
- approval note recorded

## Rejection rules
Reject if:
- unreadable source
- wrong facility
- missing period
- contradictory unit values
- duplicate import candidate
