# oka-support-desk — POC Support Engineer UCit

POC of a **Support Engineer UCit** position on the **OKA** platform
(analytical and HPC supervision). It simulates a portfolio of **8 client tickets**
processed with a reproducible method, **8 AI + HITL tools** and a **Gradio interface**
to manipulate them. It also covers portals, remote 2D/3D visualization, Linux/Windows,
AWS and technical English writing.

AI prepares, engineer validates: no automatic action on a client platform.

---

## Table of Contents

1. [Context](#1-context)
2. [Quick Start](#2-quick-start)
3. [Gradio Interface](#3-gradio-interface)
4. [What the POC Contains](#4-what-the-poc-contains)
5. [The 8 Tickets](#5-the-8-tickets)
6. [Method and AI + HITL Approach](#6-method-and-ai--hitl-approach)
7. [What it Demonstrates](#7-what-it-demonstrates)
8. [Tests and CI](#8-tests-and-ci)
9. [Assumed Limits](#9-assumed-limits)
10. [References](#10-references)

---

## 1. Context

**Target position:** **Support Engineer** — UCit (Montpellier)

**Product:** **OKA** — Data Science platform for HPC environments

https://oka.how | https://doc.oka.how

The POC demonstrates the ability to:

- read and understand OKA extensibility repositories
- qualify, diagnose and solve client tickets
- respect `HealthCheckRule`, `DataEnhancer` and webhook contracts
- capitalize via a method and reusable tools
- keep a human in the loop at every step.

### UCit Profile Coverage

| Position Mission | Proof in POC |
|---|---|
| Remote 2D/3D Visualization and HPC/IA Portals | `TICKET-008`: TurboVNC/VirtualGL runbook, Nginx, AWS ALB, branding and IP restriction |
| CCME and OKA Support | OKA: tickets 001 to 007; CCME: `docs/ccme_deployment_checklist.md` (partial) |
| N1/N2 Incidents, Management and Escalation | 8 tickets, `ticket_classifier`, `diagnostic_helper`, `ticket_prioritizer`, `docs/escalation_matrix.md` |
| Automation, Training, R&D and Tests | 8 tools, Gradio interface, `TICKET-007`, `rnd_feedback_analyzer`, `tests/` and CI |

The complete matrix, with honest limits, is in
[`docs/profile_alignment.md`](docs/profile_alignment.md).

---

## 2. Quick Start

**Prerequisites:** Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies (gradio, pytest, ruff)
make install

# Launch Gradio interface
make ui
```

The interface is available at **http://127.0.0.1:7860**.

To expose it on a different network interface:

```bash
GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7860 make ui
```

To enable basic HTTP authentication:

```bash
GRADIO_AUTH="support:password" make ui
```

Useful commands:

```bash
make lint    # ruff on tools, tests, tickets, app.py and interface_cli.py
make test    # pytest
make demo    # quick CLI demo of three tools
```

The CLI is also available as a fallback:

```bash
uv run python interface_cli.py
```

---

## 3. Gradio Interface

`app.py` exposes the 8 tools in **8 tabs** and systematically displays the
HITL banner and the tool's output log.

| Tab | Exposed Tool | Input | Output |
|---|---|---|---|
| Home & Tickets | `ticket_prioritizer.py` + Ticket reader | Ticket or full portfolio | Ticket deliverables, prioritization table |
| Profile & Evidence | `docs/profile_alignment.md` | — | Missions/evidence matrix and limits |
| 1 · Qualify | `ticket_classifier.py` | Pasted request or `request.md` | JSON family, severity, component, confidence |
| 2 · Diagnose | `diagnostic_helper.py` | Family + component | Markdown checklist of verifications |
| 3 · Respond | `response_generator.py` | Content of a `diagnosis.md` | Draft response with DRAFT banner |
| 4 · Generate Rule | `rule_generator.py` | French request, domain, name | `HealthcheckRule` skeleton for 9 domains + checklist of 5 patterns |
| 5 · Train | `training_generator.py` | — | 3-module training path |
| 6 · Analyze RND Feedback | `rnd_feedback_analyzer.py` | — | RND irritants |
| 7 · Home | — | — | Home page |

### Additional Features

- **HITL Banner**: Each tool displays a HITL warning before execution
- **LLM Local Option**: `tools/llm_client.py` + Ollama `qwen2.5-coder:7b`: domain/suggestion, JSON strict format, heuristic fallback
- **Rule Generation anchored on real sources**: `rule_generator.py`: 9 OKA domains, real providers/methods (`scan_jobs`, `get_core_load`, `get_congestion_metrics`...), ratio/percent/absolute thresholds and provider control in `llms.txt`
- **Public Contracts**: `tools/contract_context.py`: reading of `llms.txt`, drift report, broken links detection
- **Contract Tests**: 100 tests: compilation, AST, `TypeError` without `params_model`, tools, interface, auth, `llms.txt` consistency, Ollama client
- **Rule Generator LLM Test**: Qwen suggestion, keyword priority, validation and threshold normalization, plausibility guard and heuristic fallback

**100 tests pass** with `make test`. The `llms.txt` tests are ignored if the
`../oka_*` repositories are absent; set `OKA_SOURCE_ROOT` to enable them.
GitHub Actions CI runs `uv sync`, `ruff` then `pytest` on each push and pull request.

---

## 4. What the POC Contains

### 8 Client Tickets

Each ticket follows the same structure:

- `request.md`: Original request
- `qualification.md`: Qualification details
- `diagnosis.md`: Diagnosis
- `lessons.md`: Lessons learned
- `response.md`: Response
- `resolution/`: Resolution scripts

Tickets cover various scenarios:

- **TICKET-001-quota-account**: Account quota configuration
- **TICKET-002-rule-not-firing**: Rule not firing
- **TICKET-003-false-positives**: False positives
- **TICKET-004-custom-cost**: Custom cost enhancer
- **TICKET-005-missing-co2-data**: Missing CO2 data
- **TICKET-006-slack-not-working**: Slack not working
- **TICKET-007-training-request**: Training request
- **TICKET-008-visualization-portal**: Visualization portal

### 8 AI + HITL Tools

| Tool | Description |
|---|---|
| `ticket_classifier.py` | Classification (family, severity, component, confidence) |
| `diagnostic_helper.py` | Diagnosis checklist of verifications |
| `response_generator.py` | Client response draft (HITL) |
| `rule_generator.py` | Conformant HealthCheck rule generation |
| `ticket_prioritizer.py` | Prioritization by ROI |
| `automation_identifier.py` | Automations by ROI |
| `training_generator.py` | 3-module training path |
| `rnd_feedback_analyzer.py` | R&D irritants |

### Documentation

- `METHOD.md`: 5-step method (qualify→diagnose→solve→respond→capitalize)
- `AI_METHOD.md`: AI + HITL architecture with 3 guards
- `NOTES_ANALYSIS.md`: Proof of extraction from 3 source repositories
- `escalation_matrix.md`: Escalation matrix
- `known_issues.md`: Known issues
- `profile_alignment.md`: Profile alignment matrix

---

## 5. The 8 Tickets

Each ticket has the same structure:

- `request.md`: Original request
- `qualification.md`: Qualification details
- `diagnosis.md`: Diagnosis
- `lessons.md`: Lessons learned
- `response.md`: Response
- `resolution/`: Resolution scripts (if applicable)

### Ticket Summary

| Ticket | Topic |
|---|---|
| **TICKET-001-quota-account** | Account quota configuration |
| **TICKET-002-rule-not-firing** | Rule not firing |
| **TICKET-003-false-positives** | False positives |
| **TICKET-004-custom-cost** | Custom cost enhancer |
| **TICKET-005-missing-co2-data** | Missing CO2 data |
| **TICKET-006-slack-not-working** | Slack not working |
| **TICKET-007-training-request** | Training request |
| **TICKET-008-visualization-portal** | Visualization portal |

---

## 6. Method and AI + HITL Approach

### 5-Step Method (METHOD.md)

1. **Qualify**: Determine ticket family, severity, component
2. **Diagnose**: Apply verification checklist
3. **Solve**: Generate resolution or rule
4. **Respond**: Create client response draft
5. **Capitalize**: Document and reuse

### AI + HITL Architecture (AI_METHOD.md)

- **3 Guardrails**:
  1. No automatic action without explicit human validation
  2. Traceability: Every tool output is written to a revisable file
  3. Transparency: Every tool displays a HITL warning before use

- **Workflow**: AI prepares → Engineer validates → No automatic platform action

### LLM Integration

- `tools/llm_client.py` + Ollama `qwen2.5-coder:7b`: domain suggestions, JSON strict format, heuristic fallback
- Optional: can be disabled via environment variables
- Falls back to deterministic heuristics

### Public Contracts (`tools/contract_context.py`)

- Reads `llms.txt` from source repositories
- Drift report generation
- Broken link detection
- Provider/method consistency check with source repositories

---

## 7. What it Demonstrates

- Ability to read and understand OKA extensibility repositories
- Qualification, diagnosis and resolution of client tickets
- Respect for `HealthCheckRule`, `DataEnhancer` and webhook contracts
- Capitalization via a method and reusable tools
- Human-in-the-loop at every step
- Remote 2D/3D visualization and portals (TICKET-008)
- CCME support (partial)
- Automation, training, R&D and tests
- Technical English writing

---

## 8. Tests and CI

```bash
make test
```

To inspect public contracts (if `../oka_*` repositories are present):

```bash
make contracts
```

The test suite covers:

- `test_classifier.py`: 9 ticket families, including portal/visualization and CCME
- `test_diagnostic_helper.py`: non-empty checklist for all families and components
- `test_resolution_contracts.py`: compilation, AST, `params_model` contract,
  `TypeError` at rule definition without `params_model`, enhancer contract
- `test_tools.py`: execution of 8 tools, HITL, compilable rule generation,
  real providers of 9 domains, sanitized rule names, ordered thresholds,
  training profile, prioritization columns
- `test_gradio_app.py`: interface construction, Profile tab, deliverables rendering,
  Bash/PowerShell/Nginx script coloring and optional auth
- `test_llms_contract.py`: `llms.txt` parsing, broken link detection,
  provider/method consistency with source repositories
- `test_llm_client.py`: JSON parsing, Ollama payload, simulated HTTP server,
  unavailability and environment variable configuration
- `test_rule_generator_llm.py`: Qwen suggestion, keyword priority,
  validation and threshold normalization, plausibility guard and heuristic fallback

**100 tests pass** with `make test`. The `llms.txt` tests are ignored if the
`../oka_*` repositories are absent; set `OKA_SOURCE_ROOT` to enable them.
GitHub Actions CI runs `uv sync`, `ruff` then `pytest` on each push and pull request.

---

## 9. Assumed Limits

- **No actual OKA instance**: rules are compiled and checked statically, not executed against the platform
- **Rule generator**: template with heuristics, providers aligned with `oka_healthchecks`, but thresholds and fine DTO extraction need validation
- **No OKA SDK provided**: contract testing uses a minimal stub to verify `TypeError` and `params_model` presence
- **No mandatory LLM**: deterministic heuristic fallback; Ollama/Qwen is optional, local, and must be validated by the engineer
- **TICKET-004 Enhancer**: validated statically; `pandas` is not a runtime dependency of the POC
- **Local Gradio interface**: no default authentication; `GRADIO_AUTH` enables basic auth, but a reverse proxy is required for public exposure
- **8 simulated tickets**: they demonstrate the method, not a real history
- **Portal and visualization not deployed**: the runbook and scripts are provided, but no actual AWS/GPU infrastructure is attached to the POC
- **Partial CCME**: only generic checklist, due to lack of CCME repository or instance in scope
- **Oral English not demonstrable**: technical English writing is covered by the TICKET-008 summary

---

## 10. References

- Source repositories: `../oka_healthchecks`, `../oka_dataenhancers`, `../oka_webhooks`
- Profile matrix: [`docs/profile_alignment.md`](docs/profile_alignment.md)
- OKA Documentation: https://doc.oka.how
- OKA Platform: https://oka.how
- UCit: https://ucit.fr
- POC Repository: `git@ssh.bitbucket.org:lavaud_olivier/hpc-oka-support-desk.git`
