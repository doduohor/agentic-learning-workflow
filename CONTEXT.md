# Learning System

This context defines the domain language for the Codex CLI learning system. It names the concepts used to plan, run, record, review, and repeat programming learning work.

## Language

**Learning Project**:
The top-level learning effort that holds one or more Learning Profiles and the shared study context for programming topics.
_Avoid_: course, repository, roadmap

**Learning Profile**:
The current target context that gives learning decisions their priority: target role or purpose, stack, project, constraints, current level, and job or practice requirements.
_Avoid_: target context, fixed stack, system scope

**Subject**:
A broad technology or knowledge area inside the Learning Project, such as databases, message brokers, testing, architecture, language fundamentals, or tooling.
_Avoid_: topic, module

**Topic**:
A concrete study target inside a Subject, narrow enough to have a goal, blocks, practice, questions, and completion criteria.
_Avoid_: subject, lesson

**Stable Slug**:
A durable ASCII identifier for a Topic that remains stable when the title or path changes.
_Avoid_: title, path

**Parent Topic**:
A broad overview Topic that groups smaller Topics when the original Topic becomes too large to study as one unit.
_Avoid_: subject

**Topic Index**:
The navigation artifact that lists Subjects and Topics across the Learning Project.
_Avoid_: goal, roadmap

**Topic Workspace**:
The repository directory that holds one Topic's working artifacts under the Learning Project hierarchy.
_Avoid_: repository, Obsidian note

**Learning Template**:
A reusable starter file for creating consistent Topic artifacts.
_Avoid_: old topic copy

**Block**:
A logical part of a Topic's learning map, such as mental model, worked example, failure modes, or observability.
_Avoid_: session, lesson

**Block ID**:
A short stable identifier for a Block, used when Questions, Practice Attempts, Weaknesses, and repetition records link back to it.
_Avoid_: block title

**Topic Goal**:
The control artifact for a Topic, holding its purpose, prerequisites, blocks, statuses, current block, completion criteria, and active weakness summary.
_Avoid_: notes, knowledge base

**Topic State**:
The primary lifecycle state of a Topic: intake, diagnosing, planned, learning, practicing, reviewing, completed, or paused.
_Avoid_: progress note

**Intake Topic**:
A Topic captured from a raw learner request before diagnosis and planning.
_Avoid_: planned topic

**Diagnosing Topic**:
A Topic being checked for current understanding, prerequisites, Weaknesses, and initial route shape.
_Avoid_: quiz

**Planned Topic**:
A Topic with enough diagnosis, active Weakness summary, and learning map to begin the first Block.
_Avoid_: fully specified topic

**Active Block**:
The primary Block currently driving a Topic's learning work.
_Avoid_: current session

**Block Learning Cycle**:
The orchestrated learning pass through a Block: theory, example, modified example, intentional breakage, and failure explanation.
_Avoid_: practice task, lesson script

**Topic Lifecycle Scenario**:
A repeatable user or orchestrator scenario that moves a Topic through its lifecycle while reading and updating learning artifacts under the single-writer state model.
_Avoid_: ad hoc prompt, raw slash command

**Topic Lifecycle Skill**:
A Codex skill that gives the learner a stable user-facing entry point into one or more Topic Lifecycle Scenarios while preserving the Topic Workspace ownership and gates.
_Avoid_: Agent File, slash command, raw prompt

**Block Requirement**:
Whether a Block is required for Topic completion or optional future learning.
_Avoid_: priority

**Completed Topic**:
A Topic whose required Blocks are stable, applicable real-use constraints are addressed, and no blocker Weakness remains.
_Avoid_: finished notes

**Knowledge Consolidation**:
The promotion of stable Topic Knowledge into the broader Learning Project knowledge base.
_Avoid_: note copying

**Write Automation**:
An Orchestrator-controlled workflow that performs an approved external write to Anki or Obsidian after the required checks, preview, user approval, and trace decisions are complete.
_Avoid_: card promotion, duplicate check

**Write Target**:
The external destination for Write Automation, such as Anki or Obsidian, handled independently when one destination is unavailable.
_Avoid_: source artifact

**Dry-Run Preview**:
A required no-write preview that shows the proposed target, action, content, checks, trace, and expected Topic Workspace updates before external write approval.
_Avoid_: final write

**Pending Write**:
An approved or proposed external write that cannot be completed yet because a target is unavailable, a gate is blocked, or user approval is missing.
_Avoid_: failed card

**Write Outcome**:
The durable record of what happened after Write Automation, including succeeded, partial, failed, pending, or no-op results and enough trace to make reruns safe.
_Avoid_: completion evidence

**Working Knowledge Base**:
The repository-held working layer for Topic artifacts, practice traces, questions, and evolving study state.
_Avoid_: long-term knowledge base

**Long-Term Knowledge Base**:
The Obsidian-held durable knowledge layer for stable, consolidated learning that should survive beyond a Topic workspace.
_Avoid_: working notes

**Mastery Level**:
The current depth of understanding for a Block, progressing through recognition, recall, application, transfer, production-ready when applicable, and stable.
_Avoid_: done, progress

**Completion Evidence**:
Concrete proof that a Block has reached a Mastery Level, such as a no-hint explanation, practice artifact, failure analysis, follow-up answers, recorded weaknesses, or scheduled repetition.
_Avoid_: feeling of understanding

**Entity Reference**:
A local reference that combines a stable ID with a Markdown link so both humans and agents can follow relationships between learning artifacts.
_Avoid_: bare link, bare id

**Learned Block**:
A Block that reached application-level understanding with a no-hint attempt, checked practice, failure analysis, and no blocker Weakness.
_Avoid_: completed block

**Production-Ready Block**:
A Block whose knowledge can be transferred to a realistic use scenario with relevant quality, safety, operational, compatibility, performance, or maintenance constraints addressed. This level applies when the Topic or Learning Profile makes those constraints relevant.
_Avoid_: learned block

**Stable Block**:
A Block that has survived later spaced review without key answers depending on hints.
_Avoid_: remembered block

**Session**:
A dated work pass through some part of a Topic, producing attempts, feedback, new knowledge, or follow-up questions.
_Avoid_: block, lesson

**Knowledge**:
Curated understanding that has been explained, practiced, or corrected enough to be kept as durable topic knowledge.
_Avoid_: raw notes, transcript, chat log

**Topic Knowledge Base**:
The curated knowledge artifact for a Topic, containing durable explanations, small examples, realistic-use risks or limits, and corrected misconceptions.
_Avoid_: session log, transcript

**Session Note**:
Raw or lightly structured material captured during a Session before it is curated into Knowledge.
_Avoid_: knowledge

**Question**:
A prompt used to force recall, explanation, debugging, design choice, interview response, or practice.
_Avoid_: card

**Question ID**:
A stable identifier for a Question that is referenced from practice, repetition, weaknesses, or Card Traces.
_Avoid_: question text

**Question Queue**:
The managed collection of Questions for a Topic, including type, source, linked block, status, and intended use.
_Avoid_: question dump

**Question State**:
The lifecycle of a Question as draft, active, answered, failed, promoted, archived, or rejected.
_Avoid_: done

**Practice Question**:
A Question intended to drive active practice and produce an attempt that can be checked.
_Avoid_: quiz item

**Interview Question**:
A Question intended to simulate interview pressure, follow-up reasoning, and explanation quality.
_Avoid_: practice question

**Recall Question**:
A Question intended for active retrieval during same-day or spaced review.
_Avoid_: recognition prompt

**Card Candidate**:
A Question or knowledge fragment that may become an Anki card after understanding, relevance, and duplicate checks.
_Avoid_: card

**Card Promotion**:
The acceptance of a Card Candidate into Anki after understanding, relevance, duplicate checks, and any needed user decision.
_Avoid_: automatic card creation

**Card Trace**:
The link from an Anki card or Card Candidate back to the Knowledge, Practice Attempt, Weakness, or source that produced it.
_Avoid_: tag

**Rejected Card Candidate**:
A Card Candidate deliberately not promoted, kept in the Question Queue for traceability when useful.
_Avoid_: deleted card

**Active Repetition**:
A scheduled review that requires no-hint recall, explanation, application, debugging, or transfer rather than rereading.
_Avoid_: review, rereading

**Repetition ID**:
A stable identifier for an Active Repetition record, used when Repetition Failures, Weaknesses, Topic Goals, or Completion Evidence need to reference a specific review attempt.
_Avoid_: review date

**Repetition Failure**:
A failed Active Repetition that becomes evidence for a Weakness and may lower or reopen a Block's Mastery Level.
_Avoid_: forgotten question

**Repetition Log**:
The review artifact that records scheduled active repetition, the action to perform, the result, and any new weaknesses.
_Avoid_: calendar

**Weakness**:
A typed learning problem that changes what the system should do next.
_Avoid_: mistake, gap

**Weakness ID**:
A stable identifier for a Weakness that can be referenced from Questions, Practice Attempts, Repetition Failures, and Topic Goals.
_Avoid_: weakness title

**Weakness Evidence**:
The referenced Practice Attempt, failed Question, Repetition Failure, or interview answer that justifies recording a Weakness.
_Avoid_: hunch

**Weakness Register**:
The managed collection of Weaknesses for a Topic, linking each weakness to evidence, action, severity, and status.
_Avoid_: weakness list

**Weakness Severity**:
The blocking strength of a Weakness: minor allows progress, major requires planned repair, and blocker prevents closing the Block.
_Avoid_: priority

**Gap**:
A Weakness where a required concept is missing or unknown.
_Avoid_: misconception

**Misconception**:
A Weakness where the learner has an incorrect mental model.
_Avoid_: gap

**Fragile Skill**:
A Weakness where the learner can recognize or explain something but cannot reliably apply it.
_Avoid_: gap

**Application Blind Spot**:
A Weakness where the learner misses important consequences of applying knowledge in a realistic context, such as operational, reliability, security, consistency, observability, performance, compatibility, or tool-limit consequences.
_Avoid_: production blind spot, production risk

**Practice Attempt**:
A learner's active try at code, debugging, explanation, design, or interview response that can receive feedback.
_Avoid_: answer, solution

**Practice Attempt ID**:
A stable identifier for a Practice Attempt, usually date-scoped, used as evidence for Knowledge, Weaknesses, and Card Traces.
_Avoid_: session number

**Practice Journal**:
The structured record of Practice Attempts, feedback, corrections, new knowledge, and linked weaknesses for a Topic.
_Avoid_: final answers

**Practice Artifact**:
A concrete output produced during practice, such as code, SQL, Docker files, diagrams, logs, tests, or command output.
_Avoid_: note

**Session Archive**:
An optional per-session file used only when a Topic's Practice Journal becomes too large or detailed.
_Avoid_: default session log

**Codex Session**:
A single interactive Codex CLI work run that may continue a wayfinder ticket or a Topic Workspace. It is not the same thing as a learning Session inside a Topic.
_Avoid_: Session

**Session Handoff**:
A durable continuation contract that lets a later Codex Session safely resume work from persisted files instead of relying on chat context.
_Avoid_: chat recap

**Wayfinder Handoff**:
A project-level Session Handoff recorded through the wayfinder map and decision records, covering the current ticket, closed decisions, open fog, out of scope, and next decision step.
_Avoid_: ticket summary

**Topic Handoff Note**:
An optional Topic Workspace artifact used when continuation risk is high, pointing to Topic State, Active Block, open Weaknesses, pending Source Checks, Card Candidates, Active Repetitions, Role Mode, and the next safe action.
_Avoid_: source of truth

**Machine-Readable Layer**:
Optional structured metadata added later to selected learning artifacts when automation needs it.
_Avoid_: source of truth

**Source Record**:
A record of authoritative sources, dates checked, and claims that need verification for a Topic.
_Avoid_: bibliography

**Source ID**:
A stable identifier for a Source Check or Source Record entry, used when Knowledge, Questions, Practice Attempts, or Topic Goals reference a verified or unverified claim.
_Avoid_: URL

**Authoritative Source**:
A primary or official source used to verify version-sensitive, application-sensitive, production, security, protocol, or tooling behavior claims.
_Avoid_: tutorial, blog

**Source Check**:
The act of verifying a claim against an Authoritative Source and recording the date, source, and result.
_Avoid_: web search

**Unverified Claim**:
A claim kept with an explicit `Нужно проверить` marker until a Source Check confirms or rejects it.
_Avoid_: fact

**Stale Knowledge**:
Knowledge that may be outdated because tooling behavior, versions, defaults, or guidance changed.
_Avoid_: wrong knowledge

**Agent File**:
A durable Codex custom-agent configuration artifact that describes one Physical Agent's role focus, instructions, tool assumptions, and boundaries.
_Avoid_: role, slash command

**Physical Agent**:
A concrete spawned Codex agent thread that can execute one Role Mode during a run and return results to the main session or Learning Orchestrator.
_Avoid_: role

**Role Mode**:
The explicitly selected role boundary a Physical Agent follows for one run, determining which files it reads, where it may write, and when it must return an Agent Proposal.
_Avoid_: combined permissions

**Learning Orchestrator**:
The agent role that owns Topic state, coordinates Sessions, applies accepted changes, and keeps the learning artifacts consistent.
_Avoid_: tutor, writer

**Diagnostic Agent**:
A supporting agent role that checks prerequisites, current understanding, and Weaknesses before a Topic or Block is planned.
_Avoid_: examiner

**Practice Agent**:
A supporting agent role that runs active practice and records structured Practice Attempts within its allowed boundary.
_Avoid_: solver

**Question/Card Agent**:
A supporting agent role that proposes Questions and Card Candidates after checking current knowledge and duplicates.
_Avoid_: Anki writer

**Knowledge Curator Agent**:
A supporting agent role that proposes how Session Notes and Practice Attempts should be distilled into Knowledge.
_Avoid_: note taker

**Source Agent**:
A supporting agent role that verifies source-sensitive claims and records Source Checks within its allowed boundary.
_Avoid_: web searcher

**Repetition Agent**:
A supporting agent role that schedules and records Active Repetitions within its allowed boundary.
_Avoid_: reminder

**Agent Proposal**:
A structured handoff from a supporting agent to the Learning Orchestrator, containing the checked context, proposed change, evidence, risks, and exact insertion text when needed.
_Avoid_: raw subagent output

**Agent Write Boundary**:
The rule that the Learning Orchestrator owns state-changing edits while supporting agents return summaries or narrowly scoped append-only records.
_Avoid_: full file access

**Duplicate Check**:
The review of relevant Obsidian knowledge and logically matching Anki cards before a Card Candidate is promoted or Topic Knowledge is consolidated.
_Avoid_: card creation

**Lightweight Checker**:
A read-only validation layer that checks Topic Workspace Markdown for broken Entity References, invalid IDs, ownership violations, stale links, and gate-blocking inconsistencies without introducing YAML/JSON schema.
_Avoid_: orchestrator, auto-fixer

**Checker Finding**:
A human-readable checker report item with severity and gate impact, used by the Learning Orchestrator as evidence before changing state or promoting artifacts.
_Avoid_: automatic decision

**Gate Impact**:
The specific lifecycle action that a Checker Finding blocks or does not block, such as production-ready, completed, Card Promotion, Knowledge Consolidation, handoff, or no gate.
_Avoid_: severity

**Draft Orphan**:
A draft Question, Weakness, or other learning entity that is temporarily missing required links before activation.
_Avoid_: active orphan
