# Psyche: who coordinates, and who applies the results

Checked 2026-11-16. The question: in Nous Research's Psyche, is there one orchestrator that collects and merges everyone's weights, or is the work more decentralized? Short answer, from Nous's own pages: there is a coordinator for each run, but in the documented training design the clients exchange and apply results themselves rather than the coordinator aggregating them.

## What the official pages say

- **Each run has a coordinator that holds the run's state.** The docs call it the "source of truth for global state". It is implemented as a program on the Solana blockchain for decentralized runs, or as a regular TCP server for centralized runs. The docs say the centralized version is mostly used for local test runs and as a development tool. (Source 1, Source 2)
- **The coordinator sequences the run, it does not merge weights.** It moves the run between phases (waiting for members, warmup, training, witness, cooldown), tracks participants, and provides a random seed that decides data assignment and witnesses. (Source 2)
- **Clients share results with each other.** After training, each client broadcasts its result and a cryptographic commitment to the other clients over a peer-to-peer network. In the next round, clients apply the previous round's results themselves. (Source 1, Source 3)
- **Peers do the checking.** Elected witnesses send "witness proofs" to the coordinator, which advances the round once enough proofs arrive or a timeout passes. Clients also recompute and compare results to identify malicious participants. (Source 1, Source 2)
- **Model copies come from outside the coordinator.** At the end of an epoch, some clients save a checkpoint to external storage such as Hugging Face. New joiners download that checkpoint, or in later epochs download from other clients over P2P. (Source 2, Source 3)
- **Networking is peer-to-peer.** The blog describes UDP hole-punching and the Iroh library, with peers identified by Ed25519 public keys. (Source 3)

## What to take from it

- Logical coordination and physical hosting are separate questions. The coordinator's state can live in an on-chain program (decentralized backend) or on a plain server (centralized backend). The pages describe both.
- Cloud checkpoints (for example Hugging Face) and a centralized TCP mode are part of the documented design.
- Who is allowed to join and run a given deployment depends on how that run is set up. The May 2025 blog describes the roadmap as starting with "a permissioned testnet and transitioning toward a fully decentralized environment". That is a dated statement, not a check of any live run today.
- The "gated joining" point in the main README comes from an earlier check. This check did not re-test enrollment.

## Not verified

We have not run a Psyche client, read its code, or checked how any live run is currently set up. Everything above is what Nous's pages say about the intended design, not an independent audit, and this note gives no verdict on whether the system is trustless.

## Sources

1. https://docs.psyche.network/explain/index.html
2. https://docs.psyche.network/explain/general-workflow.html
3. https://nousresearch.com/nous-psyche
