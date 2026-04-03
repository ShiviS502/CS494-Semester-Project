[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/1PuxbblI)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23406014&assignment_repo_type=AssignmentRepo)

# CustomerIntel — Multi-Agent System for Customer Feedback Analysis

**CS 494 Agentic AI | Spring 2026 | University of Illinois Chicago**

### Team Members
- Rounak Deshpande (rdeshp9@uic.edu)
- Pranshu Bansal (pbans@uic.edu)
- Shivanshi Shukla (sshuk7@uic.edu)
- Mithil Ravulapalli (vravu3@uic.edu)
- Ethan Van (evan9@uic.edu)

---

## Description

CustomerIntel is a multi-agent AI system that transforms unstructured customer feedback (reviews, support tickets, surveys) into actionable business intelligence. A pipeline of five specialized LLM-powered agents — coordinated via LangGraph — handles retrieval, diagnosis, strategy generation, and adversarial quality control.

---

### Agent Architecture

| Agent | Role | Reasoning Pattern |
|-------|------|-------------------|
| Orchestrator | Coordinates workflow, synthesizes final report | ReAct |
| Data Intelligence | RAG retrieval + sentiment analysis | ReAct + Query Refinement |
| Diagnosis | Root cause analysis | Chain-of-Thought + Self-Reflection |
| Strategy | Generates prioritized recommendations | Multi-Perspective Reasoning |
| Critic | Adversarial quality control, forces revisions | Adversarial Critique |

---

> **Status:** In-progress — Proposal milestone submission. Agent nodes are functional stubs; LLM integration is the next implementation step.
