[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/1PuxbblI)

# CustomerIntel — Multi-Agent System for Customer Feedback Analysis

**CS 494 Agentic AI | Spring 2026 | University of Illinois Chicago**

A multi-agent LLM-powered system that transforms unstructured customer feedback into actionable business intelligence through retrieval-augmented generation, chain-of-thought reasoning, and adversarial critique loops.

---

## Team Members

- **Rounak Deshpande** (rdeshp9@uic.edu) — Orchestrator, System Integration, LangGraph Pipeline
- **Pranshu Bansal** (pbans@uic.edu) — Data Intelligence Agent, RAG Pipeline, ChromaDB
- **Shivanshi Shukla** (sshuk7@uic.edu) — Diagnosis Agent, Causal Reasoning, Statistics
- **Mithil Ravulapalli** (vravu3@uic.edu) — Strategy Agent, Critic Agent, Adversarial Loop
- **Ethan Van** (evan9@uic.edu) — Frontend (Streamlit), Evaluation, Testing

---

## System Architecture

### Agent Pipeline

| Agent | Role | Reasoning Pattern | LLM Model |
|-------|------|-------------------|-----------|
| **Orchestrator** | Workflow coordination & final synthesis | ReAct | Claude Sonnet 4.6 |
| **Data Intelligence** | RAG retrieval + sentiment analysis | ReAct + Query Refinement | GPT-3.5-turbo |
| **Diagnosis** | Root cause analysis | Chain-of-Thought + Self-Reflection | Claude Sonnet 4.6 |
| **Strategy** | Recommendation generation | Multi-Perspective Reasoning | Claude Haiku 4.5 |
| **Critic** | Adversarial quality control | Socratic Questioning | Claude Sonnet 4.6 |

### Data Flow

```
User Query
    ↓
Data Intelligence (Retrieve + Sentiment Analysis)
    ↓
Diagnosis (Root Cause Analysis)
    ↓
Strategy (Generate Recommendations)
    ↓
Critic (Evaluate Quality) ←---┐
    ↓                          │
    └── If Rejected ───────────┘
    ↓
    └── If Approved → Orchestrator (Final Synthesis)
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- LangChain & LangGraph
- OpenAI & Anthropic API keys (for full LLM integration)

### Installation

```bash
git clone https://github.com/your-repo/cs494-agentic-ai-group-project.git
cd cs494-agentic-ai-group-project
pip install -r requirements.txt
```

### Run the System

```bash
# With default query
python main.py

# With custom query
python main.py --query "Why are customers leaving negative reviews?"
```

### Expected Output

The system will:
1. Retrieve customer feedback documents
2. Analyze sentiment distribution
3. Identify root causes using chain-of-thought reasoning
4. Generate prioritized recommendations
5. Perform adversarial critique (up to 3 revision cycles)
6. Synthesize a comprehensive final report

---

## Project Structure

```
customerintel/
├── __init__.py              # Package init
├── agents/
│   ├── __init__.py          # Agent exports
│   ├── orchestrator.py      # Orchestrator node
│   ├── data_intelligence.py # Data Intelligence node
│   ├── diagnosis.py         # Diagnosis node
│   ├── strategy.py          # Strategy node
│   └── critic.py            # Critic node
├── graph.py                 # LangGraph state machine
├── state.py                 # Shared state TypedDict
├── prompts.py               # LLM prompt templates
├── ingest.py                # ChromaDB ingestion pipeline
└── main.py                  # CLI entry point

requirements.txt             # Python dependencies
README.md                    # This file
.gitignore                   # Git ignore patterns
```

---

## Implementation Status

### ✅ Completed (Proposal Milestone)

- ✅ LangGraph state machine with 5 agent nodes
- ✅ Conditional routing for adversarial critique loop
- ✅ Comprehensive prompt templates for all agents
- ✅ State management via TypedDict
- ✅ ChromaDB skeleton (awaiting OpenAI embeddings)
- ✅ Functional stubs demonstrating agent behavior
- ✅ CLI entry point with sample customer feedback

### ⏳ Next Steps (Implementation Phase)

- [ ] Integrate OpenAI embeddings for ChromaDB
- [ ] Connect Claude API for Orchestrator, Diagnosis, Critic, Strategy agents
- [ ] Implement DistilBERT sentiment classifier
- [ ] Add real ChromaDB retrieval with hybrid search
- [ ] Build Streamlit frontend for visualization
- [ ] Run full 12-task evaluation suite
- [ ] Optimize LLM model selection per agent

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-your-key-here
CHROMA_PATH=./chroma_db
```

### Customization

- **Max Critic Iterations**: Edit `MAX_ITERATIONS = 3` in `graph.py`
- **Chunk Size for RAG**: Edit `CHUNK_SIZE = 500` in `ingest.py`
- **Sample Feedback**: Edit `SAMPLE_FEEDBACK` in `main.py`

---

## Evaluation Plan

The system will be evaluated on 12 diverse tasks:

### Standard Cases (4)
- T1: Identify top-3 complaint themes
- T2: Analyze sentiment trends over time
- T3: Diagnose root cause of review decline
- T4: Generate prioritized shipping recommendations

### Stress/Edge Cases (4)
- T5: Handle contradictory feedback
- T6: Respond when no relevant documents exist
- T7: Process informal language and slang
- T8: Interpret vague queries

### Robust Cases (4)
- T9: End-to-end pipeline with full reasoning trace
- T10: Critic rejection and successful revision
- T11: Multi-turn follow-up question coherence
- T12: Output quality comparison with/without Critic

### Metrics

- **Diagnosis Accuracy**: Precision, Recall, F1 vs. ground truth
- **Recommendation Quality**: Human ratings (clarity, actionability, alignment)
- **Retrieval**: Precision@K, Recall@K, MRR
- **Critic Effectiveness**: Revision count, quality delta
- **End-to-End**: Latency, user satisfaction

---

## Key Features

### 1. **Multi-Agent Coordination**
ReAct-based Orchestrator dynamically routes tasks to specialized agents based on query complexity.

### 2. **Reasoning Quality**
- Chain-of-Thought (Diagnosis Agent)
- Self-reflection with evidence validation
- Multi-perspective strategy generation

### 3. **Adversarial Quality Control**
Critic Agent uses Socratic questioning to identify logical gaps, missing cost analysis, and unaddressed root causes. Forces revisions up to 3 times.

### 4. **RAG-Grounded Output**
All insights backed by retrieved customer feedback documents with metadata tracking.

### 5. **Stateful LangGraph Pipeline**
Full traceability via shared state dictionary; supports debugging and visualization.

---

## API Specifications

### Orchestrator System Prompt

Coordinates workflow using ReAct pattern. Maintains shared context and synthesizes final response.

### Data Intelligence Reasoning

ReAct with iterative query refinement:
- Generate multiple search queries
- Re-rank by relevance
- Apply metadata filters
- Refine based on Diagnosis requests

### Diagnosis Reasoning

Five-step chain-of-thought:
1. Identify statistical patterns
2. Detect temporal correlations
3. Generate causal hypotheses
4. Self-reflect on evidence strength
5. Validate with statistical confidence scores

### Strategy Reasoning

Multi-perspective approach:
1. Generate 2+ alternatives per root cause
2. Estimate cost-benefit
3. Build impact-vs-effort matrix
4. Revise based on Critic feedback
5. Produce implementation roadmap

### Critic Evaluation

Adversarial critique with structured rubric:
- Logical consistency check
- Missing element detection
- Root cause alignment verification
- Risk mitigation assessment
- Auto-approval at max iterations

---

## Contributing

All code follows PEP 8. Each agent node includes:
- Clear docstrings (function purpose, args, returns)
- TODO comments for LLM integration points
- Error handling with graceful fallbacks
- Structured output compatible with downstream agents

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ChromaDB Vector Store](https://docs.trychroma.com/)
- [Claude API](https://docs.anthropic.com/claude/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

## Status

**Current Phase**: Proposal Milestone (Code Submission)

**Next Deadline**: Full LLM Integration & Evaluation (Week 4)

---

## Support

For questions or issues, contact the team via GitHub issues or email the course instructor.

---

**Last Updated**: April 5, 2026