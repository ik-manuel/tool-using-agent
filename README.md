# Tool-Using Agent

A production-grade AI agent that reads real filesystems, calls live web search APIs, and writes structured reports to disk. Given any project directory and an analysis goal, the agent autonomously explores the codebase, researches best practices, and delivers a professional markdown report.

This is Week 16 of a structured 24-week AI Engineering roadmap, building directly on [research-agent](https://github.com/ik-manuel/research-agent) (Week 14–15). The key advancement: every tool here operates on real systems with real side effects — no mocks.

---

## What It Does

```
$ python main.py

=== Project Analyzer CrewAI ===

Enter project path: /path/to/any/project
What do you want to analyze?: code review / security audit / suggest improvements

🚀 Starting analysis with CrewAI...

[Agent explores filesystem, reads files, searches web, writes report]

✅ Analysis complete! Check the reports/ folder.
```

The agent produces a professional markdown report containing:
- Executive Summary
- Project Structure Overview
- Key Findings with specific file references
- Strengths
- Prioritised Recommendations (Low / Medium / High effort)
- Suggested Next Steps

---

## Architecture

```
main.py  →  interactive prompt  →  ProjectAnalyzerCrew.kickoff()
                                           │
                                    agents.yaml + tasks.yaml
                                           │
                                    Senior Software Architect (Agent)
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
            List Directory           Read File              Web Search
            (real filesystem)     (real file content)    (live Tavily API)
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                           ▼
                                     Write Report
                                  (real .md file on disk)
                                           │
                                  reports/analysis_[project]_[timestamp].md
```

### Tool Execution Flow

```
Step 1: list_directory(project_path)
        → real os.walk with safety filters
        → returns full file paths for agent to use

Step 2: read_file(path) × N files
        → reads actual file content
        → enforces size limit, extension whitelist, blocked path rules

Step 3: web_search(query) × max 2 searches
        → live Tavily API call
        → returns real search results with URLs and summaries

Step 4: write_report(content, project_name)
        → writes timestamped markdown to /reports directory
        → called exactly once
```

---

## File Structure

```
tool-using-agent/
├── main.py              ← interactive CLI entry point
├── crew.py              ← ProjectAnalyzerCrew: wires YAML config to tools
├── agents.yaml          ← agent role, goal, backstory definition
├── tasks.yaml           ← task workflow with mandatory step sequence
├── tools/
│   ├── __init__.py      ← clean exports for all tools
│   ├── file_tools.py    ← ListDirectoryTool + ReadFileTool
│   ├── search_tool.py   ← WebSearchTool (Tavily)
│   └── report_tool.py   ← WriteReportTool
├── reports/             ← agent output (auto-created on first run)
├── .env
└── requirements.txt
```

---

## Tools — Real Systems, Real Side Effects

### `ListDirectoryTool`
Walks a project directory using `os.walk`. Returns a formatted tree with full absolute paths so the agent can read files without guessing.

Safety constraints:
- Blocked paths: `.env`, `.git`, `node_modules`, `__pycache__`
- Max depth: 4 levels
- Max output: 300 lines
- Returns full paths per file — eliminates hallucinated path guessing

```
Output example:
Projects Root: /path/to/project
📁 .
    📄 main.py  →  /path/to/project/main.py
    📄 agents.py  →  /path/to/project/agents.py
    📁 memory
        📄 preferences.py  →  /path/to/project/memory/preferences.py
```

### `ReadFileTool`
Reads file content with strict safety enforcement before opening anything.

Constraints enforced:
- File must exist (returns error string on failure, never raises)
- Extension must be in allowlist: `.py .php .js .ts .md .css .json .yaml .txt`
- File size must be under 50KB (prevents context window overflow)
- Path must not contain blocked keywords

### `WebSearchTool`
Calls the Tavily Search API and returns top 3 results as a formatted string. Includes Tavily's direct answer when available.

```python
response = client.search(query=query, max_results=3)
```

Replaces the mock keyword-matching search used in Weeks 13–15. Every result now comes from a live HTTP request to the real web.

### `WriteReportTool`
Writes the agent's final analysis to a timestamped markdown file in the `reports/` directory.

```
reports/analysis_research-agent_20260625_150839.md
```

Auto-creates the `reports/` directory if it doesn't exist. Prepends a metadata header (generated timestamp, project name) to every report.

---

## YAML Scaffold Pattern

This project uses CrewAI's YAML-based configuration, separating agent and task definitions from Python wiring:

```yaml
# agents.yaml
project_analyst:
  role: Senior Software Architect & Code Reviewer
  goal: >
    Thoroughly analyze the project at {project_path} based on: {analysis_goal}.
    Explore structure, review key files, research best practices,
    and deliver a professional written report.
  backstory: >
    15+ years experience across PHP, Python, and JavaScript ecosystems.
    Strictly evidence-based — never references files not personally read.
    Every finding is tied to a specific file successfully read with tools.
```

```yaml
# tasks.yaml
analyze_project:
  description: >
    MANDATORY WORKFLOW:
    Step 1: CALL List Directory with {project_path}
    Step 2: CALL Read File ONLY on files from Step 1 (max 5 files)
    Step 3: CALL Web Search for best practices (max 2 searches)
    Step 4: Write analysis based ONLY on successfully read files
    Step 5: CALL Write Report ONCE
```

`crew.py` loads these files and injects real tool instances:

```python
@CrewBase
class ProjectAnalyzerCrew:
    agents_config = "agents.yaml"
    tasks_config  = "tasks.yaml"

    @agent
    def project_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["project_analyst"],
            tools=[ListDirectoryTool(), ReadFileTool(), 
                   WebSearchTool(), WriteReportTool()],
            llm=self.llm,
            max_iter=20,
        )
```

---

## Sample Report Output

**Input:** `research-agent` project, goal: `code review`

**Agent behaviour observed:**
```
🔧 Tool: list_directory     → returned 8 real files
🔧 Tool: read_file(main.py) → returned 47 lines of real code
🔧 Tool: read_file(tools.py)→ returned mock search implementation
🔧 Tool: web_search         → "python code review best practices"
🔧 Tool: write_report       → saved to reports/
```

**Report excerpt:**
```markdown
## Areas for Improvement

### Duplicate Mock Data Entry
In tools.py, the same entry appears twice:
{"title": "AI Agents Transforming Software Development 2024", ...}

Recommendation: Remove the duplicate to maintain data integrity.

### Hardcoded Delay
time.sleep(10) in main.py is hardcoded.
Recommendation: Make configurable via environment variable:
    delay = int(os.getenv("RESEARCH_DELAY", 10))
```

Every finding in the report referenced real code from real files — no fabricated content.

---

## How to Run

### 1. Clone and set up

```bash
git clone https://github.com/ik-manuel/tool-using-agent
cd tool-using-agent

python3 -m venv venv
source venv/bin/activate

python3 -m pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
MODEL=groq/qwen/qwen3-32b
# Optional - if using Ollama locally
OLLAMA_HOST=http://localhost:11434
```

Get API keys:
- Groq: [console.groq.com](https://console.groq.com) — free tier
- Tavily: [tavily.com](https://tavily.com) — 1,000 free searches/month

### 3. Apply the cache_breakpoint patch

CrewAI injects an Anthropic-specific field that Groq rejects. The patch is applied automatically in `main.py`:

```python
# main.py — applied before any crewai imports
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg
```

See Engineering Decisions for full context.

### 4. Run

```bash
python main.py
```

Enter any local project path when prompted. The agent works on PHP, Python, JavaScript, or any project containing supported file types.

---

## Demo Scenarios

```bash
# Code review
Enter project path: /path/to/research-agent
What to analyze?: code review

# Security audit  
Enter project path: /path/to/laravel-app
What to analyze?: security audit

# Improvement suggestions
Enter project path: /path/to/any-project
What to analyze?: suggest improvements

# Architecture review
Enter project path: /path/to/complaint-ai
What to analyze?: architecture review and scalability
```

---

## Engineering Decisions

### Tool Permission Model

All file tools enforce explicit permissions before any operation:

```
READ allowed:   .py .php .js .ts .md .css .json .yaml .txt
READ blocked:   .env, .git, node_modules, __pycache__
SIZE limit:     50KB per file (prevents context window overflow)
DEPTH limit:    4 directory levels
WRITE allowed:  /reports directory only
```

This is not optional safety theatre — it's the production pattern. An agent with unrestricted write access will eventually write somewhere it shouldn't. Constraining the blast radius upfront prevents data loss.

### Full Paths in Directory Listing

Early testing showed the agent hallucinating file paths — reading `config.json`, `__init__.py`, and `utils.py` that don't exist, then fabricating findings about them.

Root cause: the agent inferred "typical Python project" file structure from training data rather than reading the actual directory output.

Fix: `ListDirectoryTool` returns full absolute paths per file:
```
📄 main.py  →  /absolute/path/to/main.py
```

The agent copies the exact path rather than constructing one from memory. Hallucinated file reads dropped to zero after this change.

### cache_breakpoint Monkey-Patch

CrewAI injects an Anthropic-specific `cache_breakpoint` field into system messages. Groq rejects this with a 400 error. This is an open bug as of CrewAI 1.14.4 (GitHub issue #5886).

The fix is a one-line monkey-patch applied before any CrewAI imports:

```python
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg
```

This is superior to editing installed package files because it survives `pip install --upgrade` and is visible in source code.

### max_iter=20 for File Analysis

Initial testing used `max_iter=5` (the research-agent default). File analysis consistently hit the limit before completing:

```
list_directory    → 1 iteration
read_file × 5    → 5 iterations
web_search × 2   → 2 iterations
synthesise        → 2-3 iterations
write_report      → 1 iteration
─────────────────────────────────
Total needed:      12-15 iterations
```

`max_iter=20` allows complete analysis without truncation while still providing a safety ceiling.

### Tavily over Mock Search

Weeks 13–15 used a keyword-scored mock search tool. Week 16 replaces it with live Tavily API calls. The key differences in production:

| Aspect | Mock (Weeks 13-15) | Tavily (Week 16) |
|---|---|---|
| Results | Hardcoded strings | Real web content |
| Relevance | Keyword overlap scoring | Semantic search |
| Freshness | Static | Current as of request |
| Failure modes | Always succeeds | Network errors, rate limits |
| Token cost | Minimal | Scales with result length |

Error handling: all failures return a string `"Search failed: {reason}"` rather than raising — the agent reads the error and adapts rather than crashing.

### YAML Scaffold vs Explicit Python

Weeks 14–15 used explicit Python for agent/task definition. Week 16 uses CrewAI's YAML scaffold pattern. Tradeoff:

```
Explicit Python:  fully transparent, easier to debug
YAML scaffold:    cleaner config, better for multi-agent (Week 17)
                  separation of concerns between config and wiring
```

YAML is preferred from Week 16 onward because multi-agent systems (Week 17) benefit from having agent roles defined declaratively rather than embedded in Python logic.

---

## Stack

- **Language:** Python 3.12
- **Framework:** CrewAI 1.14.7
- **LLM:** qwen/qwen3-32b or qwen3-coder:480b-cloud via Groq/Ollama
- **Search:** Tavily Search API
- **LLM Routing:** LiteLLM (via CrewAI)
- **Environment:** python-dotenv

---

## Roadmap Context

| Week | Project | Concept |
|---|---|---|
| 13 | single-agent-system | ReAct agent from scratch (PHP) |
| 14 | research-agent | CrewAI framework, mock tools |
| 15 | research-agent | Custom memory layer |
| **16** | **tool-using-agent** | **Real tools: filesystem, live search, report writing** |
| 17 | multi-agent-team | Multi-agent orchestration |

The progression from Week 13 to Week 16:
```
Week 13: built the loop manually (while loop, PHP)
Week 14: let the framework run the loop (CrewAI, mock tools)
Week 15: gave the agent memory across sessions
Week 16: gave the agent real capabilities with real side effects
```

---

## Author

**Ikechukwu Manuel** — Backend Developer transitioning to AI Engineer.
Building in public through a structured 24-week roadmap.

[GitHub](https://github.com/ik-manuel) · [LinkedIn](https://linkedin.com/in/ik-manuel)