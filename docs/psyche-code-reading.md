# Psyche: reading the code for who applies the results (supplement)

Status: read from public source at commit 0bdb13d of PsycheFoundation/psyche on 2026-11-16. Read only; not built or run. Complements the docs-based topology note; code can change after this commit.

## What the code shows
- Applying results happens inside the client. In `shared/client/src/state/train.rs`, `apply_results` takes the commitments the client received and the payloads it holds, chooses which commitment counts, and then calls `trainer.optimize(...)` on its own trainers. https://raw.githubusercontent.com/PsycheFoundation/psyche/0bdb13d/shared/client/src/state/train.rs
- The choice uses `Coordinator::select_consensus_commitment_by_witnesses` in `shared/coordinator/src/coordinator.rs`. It scores each commitment by how many witnesses' bloom filters contain its data hash, keeps those meeting the witness quorum, and returns the highest score. https://raw.githubusercontent.com/PsycheFoundation/psyche/0bdb13d/shared/coordinator/src/coordinator.rs
- The function is a plain deterministic function of the commitments, witnesses and quorum, so clients that hold the same coordinator state would compute the same choice.

## Reading, with limits
This supports the docs' description that clients apply results themselves and that witnesses help decide which results count. It does not show how witness data reaches each client, how the Solana program stores run state, or whether a given live run is permissioned. Those were not checked.
