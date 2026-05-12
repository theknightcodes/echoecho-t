# Architecture Decision Records

## DamyDream — Decision Log

---

## ADR-001: Python + Desktop First

**Status:** Accepted  
**Date:** 2026-05-13  
**Context:** Need to validate the core audio + AI pipeline before committing to mobile development.  
**Decision:** Start with Python desktop prototype (Phase 1) before Flutter mobile (Phase 2).  
**Consequences:** (+) Fast iteration, rich debugging, no mobile toolchain complexity. (−) Requires rewrite for mobile; mitigate by keeping pipeline logic modular.

---

## ADR-002: ONNX Runtime as Primary Inference Engine

**Status:** Proposed  
**Date:** 2026-05-13  
**Context:** Need a single inference runtime that works on desktop and mobile.  
**Decision:** Standardize on ONNX Runtime (desktop) and ONNX Runtime Mobile (Android).  
**Consequences:** (+) Single model format, quantization tools, active Microsoft support. (−) Some models (Whisper) need community ONNX conversions; llama.cpp may supplement for LLMs.

---

## ADR-003: Flutter + Kotlin Hybrid Mobile App

**Status:** Proposed  
**Date:** 2026-05-13  
**Context:** Need cross-platform UI with access to low-level Android audio APIs.  
**Decision:** Flutter for UI and state management; Kotlin native modules for audio, Bluetooth, and background services.  
**Consequences:** (+) Future iOS port with minimal UI work. (−) FFI bridge complexity; requires careful threading.

---

## ADR-004: Offline-First, Cloud Optional

**Status:** Proposed  
**Date:** 2026-05-13  
**Context:** Latency, privacy, and cost all favor on-device processing.  
**Decision:** All core inference runs on-device. Cloud APIs are opt-in per session, never default.  
**Consequences:** (+) Works everywhere, no privacy concerns, predictable cost. (−) Model size constraints on mobile; requires aggressive quantization.

---

## ADR-005: Phone as Compute Hub, Wearable as I/O Peripheral

**Status:** Proposed  
**Date:** 2026-05-13  
**Context:** Custom wearable hardware is expensive and risky for early phases.  
**Decision:** Smartphone handles all AI inference; wearable (Phase 4+) is microphone + BLE transmitter only.  
**Consequences:** (+) Faster iteration, no thermal/battery constraints on wearable. (−) Requires phone nearby; future hybrid architecture may distribute inference.

---

## Template for Future ADRs

```markdown
## ADR-NNN: Title

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]
**Date:** YYYY-MM-DD
**Context:** What is the issue that we're seeing that is motivating this decision or change?
**Decision:** What is the change that we're proposing or have agreed to implement?
**Consequences:** What becomes easier or more difficult to do because of this change?
```
