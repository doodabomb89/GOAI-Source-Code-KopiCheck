# KopiCheck

A passive, closed loop compliance agent for hawker stalls.

## One Liner

KopiCheck watches and listens during service through a stall owner's phone camera and microphone, and turns that into a completed NEA food safety compliance log by the end of the day, without the owner ever stopping to type, tap, or photograph anything.

## Problem

NEA hygiene compliance requires temperature checks, cleaning schedules, and cross contamination avoidance to be logged consistently throughout the day. Hawker stall owners run continuous service with no spare hands for admin, so logging is often skipped or reconstructed from memory afterward, both of which create real audit risk and threaten the stall's public hygiene grade.

## System Architecture

KopiCheck runs a five stage closed loop:

1. **User Input Handling.** Key frames are sampled from the stall camera feed every few seconds, or on a motion or audio trigger, rather than streaming continuous raw video. Ambient audio is captured in parallel.
2. **Task Understanding.** Each sampled frame is classified against NEA checklist categories using Qwen3-VL. Qwen3-Omni fuses audio with vision for ambiguous cases, such as a verbal cue that a cleaning task has just been completed.
3. **Workflow Orchestration.** Schedule driven prompts (fixed interval checks) run alongside event driven flags (a detected hazard). The agent decides whether to log an event silently, nudge the owner, or queue it for human confirmation.
4. **Knowledge Base.** NEA's published self checklist categories, temperature gauges on refrigerators and chillers, cleaning schedules, pest control frequency, and food hygiene certification, form the grounding ruleset every detected event is checked against.
5. **Result Delivery.** At the end of the service day, all logged events are compiled into an NEA format compliance log for the owner to review and approve.

## Models Used

* **Qwen3-VL** (open source, Alibaba Cloud / Qwen team): vision reasoning over sampled key frames, used to classify frames against compliance categories.
* **Qwen3-Omni** (open source, Alibaba Cloud / Qwen team): real time audio and vision fusion, used for the agent's spoken prompts and for interpreting verbal narration during service. Chosen for its low response latency among open source options.

Both models are open source, self hostable, and fine tunable without vendor lock in, which fits a cost sensitive small business product and aligns with GOAI's open source positioning.

## Privacy and Security

* No raw video or audio is retained. Sampled frames are processed for compliance events and discarded immediately. Only the extracted event (for example, "temp check logged 2:04pm") persists.
* No facial recognition. Detection is scoped to food safety relevant surfaces and objects, not to identifying customers or staff.
* Camera and microphone are only active during hours the stall owner explicitly declares as service hours.
* The compiled end of day log is a draft. It does not become the official compliance record until the owner reviews and confirms it.

## What's In This Repository
