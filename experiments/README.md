# experiments

Not a tutorial step. Scratch files kept for reference.

## What's here
- `test_key.py` — smallest possible call; confirms `GROQ_API_KEY` works.
- `list_models.py` — dumps the model ids the endpoint offers.
- `see_chunks.py`, `streaming_test.py`, `temp_experiment.py` — Day 1
  streaming pokes: what a streamed response looks like chunk by chunk.

## How to run
```
python experiments/test_key.py
```
All read `GROQ_API_KEY` from the repo-root `.env`.
