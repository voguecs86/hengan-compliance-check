# HengAn AI Compliance Pass

> Free EU AI Act compliance checker for startups, SaaS founders, and indie hackers. 5 minutes. No signup. Open source.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://voguecs86.github.io/hengan-compliance-check/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/voguecs86/hengan-compliance-check)

---

## TL;DR

**EU AI Act Article 50 enforcement starts August 2, 2026. If your product generates AI content and has European users, you need to comply — or face fines up to 15 million euros.**

Use this free tool to figure out where you stand in 5 minutes.

---

## Why This Matters

| Deadline | Requirement | What It Means |
|----------|-------------|---------------|
| **July 22, 2026** | EU AI Code of Conduct signing closes | Sign to get "presumption of conformity" protection |
| **August 2, 2026** | Article 50 full enforcement begins | All AI-generated content must be clearly labeled for EU users |
| December 2, 2026 | C2PA watermark mandate | AI-generated content must embed verifiable C2PA digital signatures |
| **Max Penalty** | 15M EUR or 3% global annual turnover | Whichever is higher |

**Who is affected?** Anyone deploying AI systems that generate content shown to EU users — SaaS platforms, e-commerce sites, content tools, chatbot interfaces, social media apps.

---

## What This Tool Does

### 1. Compliance Self-Assessment (3 minutes)
Answer 5 straightforward yes/no questions:
- Does your product generate AI content?
- Do you have EU-based users?
- Do you currently label AI-generated content?
- Have you signed the EU AI Code of Conduct?
- Do you maintain content provenance records?

**Instant result: High / Medium / Low risk rating with a personalized action checklist.**

### 2. C2PA Technical Reference
Ready-to-use C2PA implementation resources:
- **c2patool** — CLI for signing and verifying C2PA manifests
- **c2pa-python** — Python bindings for programmatic signing
- **c2pa-js** — Browser-side C2PA manifest reader
- **EU AI official label icons** — Ready-to-use SVG badges
- **Code of Conduct signing template** — Fill-and-submit guide

All tools are Apache 2.0 / MIT licensed. Zero cost, production-ready.

### 3. 5-Week Compliance Sprint Roadmap
A week-by-week action plan from now to August 2, designed for small teams:
- Week 1: Scope assessment + team briefing
- Week 2: Labeling implementation (frontend + API)
- Week 3: C2PA integration kickoff
- Week 4: Code of Conduct signing + compliance reporting
- Week 5: Final testing + go-live checklist

### 4. Zero-Cost by Design
- GitHub Pages hosted — free forever
- Pure HTML/CSS/JS — no backend, no database
- No signup required — your data never leaves your browser
- Entire tool is a single `index.html` file

---

## Quick Start

### Online
Visit **[https://voguecs86.github.io/hengan-compliance-check/](https://voguecs86.github.io/hengan-compliance-check/)**

### Local
```bash
git clone https://github.com/voguecs86/hengan-compliance-check.git
cd hengan-compliance-check
open index.html   # or double-click in your file explorer
```

No build tools. No dependencies. Just open and use.

---

## Project Structure

```
hengan-compliance-check/
  index.html        — Main page (compliance checker + solution intro + FAQ)
  README.md         — Chinese documentation
  README_EN.md      — This file (English)
  LICENSE           — MIT License
  .gitignore
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vanilla HTML/CSS/JS |
| Deployment | GitHub Pages (free) |
| C2PA Detection | c2pa-js (browser-side, planned integration) |
| Total Cost | $0 |

---

## Roadmap

| Milestone | Target | Deliverables |
|-----------|--------|--------------|
| **v1.0 MVP** | Jul 1, 2026 | Compliance self-check + C2PA tech reference + Code of Conduct guide |
| **v1.1** | Jul 8, 2026 | EU AI Act compliance handbook (EN) + industry use cases |
| **v1.2** | Jul 15, 2026 | C2PA signing tool integration + compliance report generator (PDF) |
| **v2.0** | Jul 22, 2026 | Official ProductHunt launch + multi-language support |
| **Pro Edition** | Aug 2, 2026 | Batch signing API + enterprise compliance dashboard |

---

## FAQ

**Q: Is this tool really free?**
A: Yes. Completely free. No premium tier. No data collection. The Lite version will always be free and open source. (A Pro edition with batch processing and enterprise features will be available separately.)

**Q: Do I need a lawyer to use this?**
A: This tool helps you self-assess your compliance readiness. It is NOT a substitute for legal advice. If you serve EU users at scale, consult an EU data protection lawyer.

**Q: What if I only have a few EU users?**
A: The regulation applies regardless of scale. Even one EU user triggers compliance obligations. The self-assessment will tell you exactly what applies to your situation.

**Q: Can I contribute?**
A: Absolutely! PRs are welcome. See [Contributing](#contributing) below.

**Q: I'm a solo developer / indie hacker. Is this for me?**
A: Yes. This tool was built specifically for small teams and solo founders who can't afford enterprise compliance suites. 5 minutes, no jargon, actionable output.

**Q: What's the difference between August 2 and December 2 deadlines?**
A: August 2 = you must *label* AI-generated content clearly. December 2 = you must *embed C2PA digital signatures* into the content files themselves. Think of it as "phase 1: tell users" and "phase 2: prove it cryptographically."

---

## Contributing

Issues and pull requests are welcome!

Current priority areas:
- English translation and localization
- C2PA signing function integration (c2pa-js / c2pa-python)
- Compliance report PDF generation
- Industry-specific compliance scenarios (e-commerce, SaaS, content platforms)
- Accessibility improvements

Please open an issue to discuss your ideas before submitting large PRs.

---

## About HengAn AI

HengAn AI is a bootstrapped startup focused on making cutting-edge AI capabilities accessible and practical for real-world businesses. We build zero-cost, open-source tools that solve immediate problems — starting with AI compliance for the global developer community.

- **Mission**: Democratize access to AI infrastructure tools
- **Approach**: Open source first, zero-cost by design, practical over theoretical
- **Contact**: [hengan-ai@proton.me](mailto:hengan-ai@proton.me)

---

## Disclaimer

This tool provides informational self-assessment only. It does **not** constitute legal advice. EU AI Act compliance requirements vary by jurisdiction, product type, and user base. Always consult a qualified EU data protection lawyer for your specific situation.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Links

- **Live Tool**: [https://voguecs86.github.io/hengan-compliance-check/](https://voguecs86.github.io/hengan-compliance-check/)
- **GitHub**: [https://github.com/voguecs86/hengan-compliance-check](https://github.com/voguecs86/hengan-compliance-check)
- **EU AI Act Full Text**: [https://artificialintelligenceact.eu/](https://artificialintelligenceact.eu/)
- **C2PA Specification v2.2**: [https://c2pa.org/specifications/specifications/2.2/](https://c2pa.org/specifications/specifications/2.2/)
- **EU AI Pact (Code of Conduct)**: [https://digital-strategy.ec.europa.eu/en/policies/ai-pact](https://digital-strategy.ec.europa.eu/en/policies/ai-pact)

---

*README version: v1.0 | Last updated: 2026-06-27 | Maintainer: HengAn AI Team*
