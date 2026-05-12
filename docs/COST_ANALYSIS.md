# Cost Analysis & Budget

## EchoEcho-T — AI Communication Companion

---

## Cost Philosophy

- **Phase 1:** Spend nothing. Use existing hardware and free/open-source software.
- **Phase 2:** Buy only what is absolutely necessary (phone + earbuds).
- **Phase 3+:** Cloud costs only for optional fallbacks; default is offline.
- **Phase 4:** Hardware prototyping budget; manufacturing is a future decision.

---

## Phase 0 — Foundation Learning

| Item | Cost (SGD) | Notes |
|---|---|---|
| Software | $0 | Python, Flutter, ONNX Runtime — all free |
| Learning resources | $0 | Documentation, GitHub repos, YouTube |
| Existing laptop | $0 | Already owned |
| **Phase 0 Total** | **$0** | |

---

## Phase 1 — Desktop Prototype

| Item | Cost (SGD) | Notes |
|---|---|---|
| Software | $0 | faster-whisper, sounddevice, piper-tts, Silero VAD — all open-source |
| APIs | $0–50 | Optional: test cloud STT/translation for comparison |
| USB microphone (optional) | $50–150 | Better audio for desktop testing; laptop mic works too |
| Cloud compute (optional) | $0 | Run everything locally |
| **Phase 1 Total** | **$0–200** | |

### Phase 1 Cost Scenarios

| Scenario | Cost | When |
|---|---|---|
| Minimal | $0 | Use laptop mic, all local, no APIs |
| Recommended | $50 | USB mic for better test quality |
| Max | $200 | USB mic + API credits for benchmarking |

---

## Phase 2 — Mobile MVP

| Item | Cost (SGD) | Notes |
|---|---|---|
| Android flagship phone | $900–1,500 | Samsung S24, OnePlus 13, or Pixel 9 Pro |
| Bluetooth earbuds | $50–300 | Sony WF series, Nothing Ear, Pixel Buds |
| APIs (optional) | $50/month | OpenAI, Gemini, or Deepgram for cloud fallback |
| Flutter dev tools | $0 | Free |
| **Phase 2 Total (one-time)** | **$950–1,800** | |
| **Phase 2 Total (monthly)** | **$0–50** | Optional APIs only |

### Recommended Phase 2 Setup

| Component | Recommendation | Cost |
|---|---|---|
| Phone | Samsung S24 or OnePlus 13 | $1,000 |
| Earbuds | Nothing Ear (a) or Sony WF-1000XM5 | $150 |
| Optional cloud credits | Deepgram STT or Whisper API | $50/mo |
| **Recommended Total** | | **$1,150 + $50/mo** |

### Budget-Conscious Phase 2 Setup

| Component | Recommendation | Cost |
|---|---|---|
| Phone | Used Pixel 7 Pro or mid-range Samsung | $500 |
| Earbuds | Generic Bluetooth earbuds | $50 |
| Cloud | None (offline only) | $0 |
| **Budget Total** | | **$550** |

---

## Phase 3 — AI Reply Assistant

| Item | Cost (SGD) | Notes |
|---|---|---|
| Cloud inference | $50–300/month | OpenAI, Gemini, or Claude API for complex queries |
| Vector database | $0–20/month | Optional: Supabase pgvector or Pinecone free tier |
| Backend hosting | $0–30/month | Optional: FastAPI on Render, Supabase, or Firebase |
| Local LLM compute | $0 | Runs on phone (offline) |
| **Phase 3 Total (monthly)** | **$50–350** | |

### Phase 3 Cost Scenarios

| Scenario | Monthly Cost | Description |
|---|---|---|
| Offline-only | $0 | All inference on phone; no cloud |
| Light cloud | $50 | Occasional complex queries via API |
| Heavy cloud | $300 | Frequent cloud LLM use, vector DB, hosting |
| Recommended | $50–100 | Light cloud with local as default |

---

## Phase 4 — Wearable Device

| Item | Cost (SGD) | Notes |
|---|---|---|
| Dev kits / prototyping | $100–500 | ESP32-S3, Raspberry Pi Zero 2W, microphone modules |
| Microphone arrays | $50–200 | Knowles, InvenSense evaluation kits |
| Battery + power management | $50–150 | Li-Po cells, charging modules |
| PCB prototyping | $100–300 | JLCPCB or Oshpark small runs |
| 3D printing / enclosures | $50–200 | Local makerspace or online services |
| Testing equipment | $0–200 | Multimeter, oscilloscope (optional) |
| **Phase 4 Total (prototyping)** | **$350–1,550** | |

### Manufacturing Cost Estimate (Future)

| Scale | Per-Unit Cost | Setup Cost | Notes |
|---|---|---|---|
| 10 units (hand-assembled) | $50–100 | $0 | Dev kit based |
| 100 units (small batch) | $30–60 | $2,000–5,000 | Custom PCB, assembled |
| 1,000 units | $15–30 | $10,000–20,000 | Factory assembly |
| 10,000+ units | $8–15 | $50,000+ | Injection molding, mass production |

---

## Phase 5 — Autonomous Conversational Agent

| Item | Cost (SGD) | Notes |
|---|---|---|
| Cloud infrastructure | $100–500/month | If heavy cloud dependency |
| Storage | $20–50/month | Conversation persistence |
| Analytics | $0–30/month | Optional: Amplitude, Mixpanel |
| **Phase 5 Total (monthly)** | **$120–580** | |

---

## Cumulative Project Cost

### Minimal Budget (Offline-First, Conservative)

| Phase | One-Time | Monthly |
|---|---|---|
| Phase 0 | $0 | $0 |
| Phase 1 | $0 | $0 |
| Phase 2 | $550 | $0 |
| Phase 3 | $0 | $0 |
| Phase 4 | $350 | $0 |
| **Total Through Phase 4** | **$900** | **$0** |

### Recommended Budget (Balanced)

| Phase | One-Time | Monthly |
|---|---|---|
| Phase 0 | $0 | $0 |
| Phase 1 | $50 | $0 |
| Phase 2 | $1,150 | $50 |
| Phase 3 | $0 | $100 |
| Phase 4 | $800 | $0 |
| **Total Through Phase 4** | **$2,000** | **$150/mo** |
| **6-month run rate (Phases 2–4)** | | **$900** |
| **Grand Total (10 months)** | **$2,000** | **$1,500** |
| **Combined** | | **$3,500** |

### Maximum Budget (Cloud-Heavy, Premium Hardware)

| Phase | One-Time | Monthly |
|---|---|---|
| Phase 0 | $0 | $0 |
| Phase 1 | $200 | $0 |
| Phase 2 | $1,800 | $50 |
| Phase 3 | $0 | $350 |
| Phase 4 | $1,550 | $0 |
| **Total Through Phase 4** | **$3,550** | **$400/mo** |
| **6-month run rate (Phases 2–4)** | | **$2,400** |
| **Grand Total (10 months)** | **$3,550** | **$4,000** |
| **Combined** | | **$7,550** |

---

## Cost Optimization Strategies

### Reduce Phase 2 Costs
- Buy a used Android phone instead of new (-$400–600)
- Use existing Bluetooth earbuds (-$150)
- Skip cloud APIs entirely (-$50/mo)

### Reduce Phase 3 Costs
- Use only local LLMs (-$50–300/mo)
- Self-host backend on home server (-$30/mo)
- Use Supabase free tier (-$20/mo)

### Reduce Phase 4 Costs
- Use Raspberry Pi Zero 2W instead of custom PCB (-$100–200)
- 3D print at a makerspace (-$50–100)
- Limit to 2–3 prototype iterations (-$100–200)

---

## Funding Checklist

| Milestone | Suggested Funding | Use Of Funds |
|---|---|---|
| Phase 0–1 | $0–200 | Software, optional USB mic |
| Phase 2 | $550–1,800 | Phone + earbuds |
| Phase 3 | $50–350/month | Cloud inference (optional) |
| Phase 4 | $350–1,550 | Prototyping hardware |
| Phase 4+ Manufacturing | $10,000–50,000 | First small batch production |

---

## Revenue / Monetization Pathways (Future)

| Model | Description | Price Point |
|---|---|---|
| App subscription | Cloud AI features, more languages | $5–15/month |
| Wearable device | Hardware sales | $100–250 one-time |
| Enterprise license | Meeting mode, team accounts | $50–100/seat/month |
| API access | Third-party integration | Usage-based |

---

## Key Takeaway

> This project can be built for **under SGD 1,000** in the first 6 months if you stay offline-first and use budget hardware. The primary cost is the Android phone for Phase 2. Everything else is optional.
