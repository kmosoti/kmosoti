# Kennedy Mosoti

**Observability platform engineer building development infrastructure for AI-assisted systems.**

[Website](https://kennedy.mosoti.dev) · [GitHub](https://github.com/kmosoti) · [Résumé](./assets/kennedy-mosoti-resume.pdf) · [Email](mailto:kennedy.rmosoti@gmail.com)

> Systems should tell on themselves.

I work where infrastructure, platform engineering, observability, and AI-assisted development meet. My professional background is in Splunk, Logstash, SaltStack, Linux, automation, incident analysis, remediation, and disaster-recovery readiness.

The current work is more foundational: I am building the development tools I want before I use them to take on harder problems, including problems outside my home domain.

## Roadmap

The roadmap has two stages.

1. **Build the development substrate.** Make repository structure, agent coordination, authority, evidence, testing, and operational state explicit.
2. **Use it beyond the substrate.** Apply those tools to unfamiliar problem domains without pretending that confidence is evidence or that an agent is its own control plane.

The tools should make it safer to enter unfamiliar territory. They should expose assumptions, preserve provenance, constrain effects, and make failure inspectable.

## Current projects

| Project | Role in the toolchain |
| --- | --- |
| [Blackcell](https://github.com/kmosoti/blackcell) | Evidence-grounded action control for LLM agents, with typed proposals, deterministic authorization, and replayable outcomes. |
| [Kernform](https://github.com/kmosoti/Kernform) | Repository-shaping and architectural-conformance engine driven by explicit, versioned forms. |
| [cognitive-miniworld](https://github.com/kmosoti/cognitive-miniworld) | Deterministic testbed for cognitive primitives and falsifiable experiments. |
| [Gordian](https://github.com/kmosoti/gordian) | Research-driven coordination substrate for software development by humans and autonomous agents. |
| [FabricO11y](https://github.com/kmosoti/FabricO11y) | Rust-first evidence runtime for ordered observations, provenance, corrections, and completeness-aware answers. |

These projects approach the same problem from different layers:

```text
repository contract  ->  coordination  ->  controlled action
        |                       |                 |
     Kernform                Gordian          Blackcell
                                |
                         evidence runtime
                                |
                           FabricO11y
                                |
                      bounded experiments
                                |
                     cognitive-miniworld
```

## Paused, not abandoned

[learning-os](https://github.com/kmosoti/learning-os) is intentionally paused while I build the AI-engineering, infrastructure, platform, and observability foundations above. It remains a candidate downstream problem for the toolchain once the substrate is mature enough to justify using it.

## Public interface

[kennedy.mosoti.dev](https://kennedy.mosoti.dev) is my authoritative website. [ui-servo](https://github.com/kmosoti/ui-servo) builds it through an interface-quality control loop: a written direction is the reference signal, browser probes are sensors, and blind cross-family critics act as comparators.

This profile repository is only the GitHub front door. The site source, build logic, and quality gates belong to `ui-servo`.

## Operational evidence

- Automated search-filter changes across more than **3,000 Splunk roles**.
- Supported Salt-based automation across more than **100 search heads**.
- Worked across Kafka, Logstash, and Splunk ingestion paths, including stale-topic cleanup and lagging consumers.
- Investigated disaster-recovery readiness gaps around cluster-manager and deployer workflows.
- Evaluated AI-generated Python, JavaScript, and SQL for correctness, maintainability, edge cases, and instruction following.

## Operating bias

- Prefer explicit contracts to inherited assumptions.
- Inspect before mutating.
- Bind claims to evidence and exact artifacts.
- Make authority narrower than capability.
- Treat observability as part of correctness, not decoration.

I am an optimistic absurdist by temperament. The boulder is real. The hill is real. The correct response is still to instrument the slope.
