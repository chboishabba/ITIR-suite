Skip to main content
[FOSS - localhost] Introducing StatiBaker (part of ITIR suite) -- Ultimate Memory Prosthetic -- Keep track of what you're doing (ideal for agentic/openclaw/moltbook) : r/selfhosted


r/selfhosted
Search in r/selfhosted
Advertise on Reddit

Open chat
1
Create
Create post
Open inbox

User Avatar
Expand user menu
Skip to NavigationSkip to Right Sidebar

Back
r/selfhosted icon
Go to selfhosted
r/selfhosted
•
2d ago
TotalEmotional9530

[FOSS - localhost] Introducing StatiBaker (part of ITIR suite) -- Ultimate Memory Prosthetic -- Keep track of what you're doing (ideal for agentic/openclaw/moltbook)
Built With AI (Fridays!)
r/selfhosted - [FOSS - localhost] Introducing StatiBaker (part of ITIR suite) -- Ultimate Memory Prosthetic -- Keep track of what you're doing (ideal for agentic/openclaw/moltbook)
github.com

Open
Hey folks,

With all the hype around OpenClaw / Clawdbot / Moltbot, Moltbook, Copilot Recall, Rewind, etc, I realised something pretty stark:

Most of these tools are either
• autonomous agents that act for you
or
• surveillance-style “memory” tools that quietly rewrite what happened
(or, in Moltbook’s case, spin up agent-native narratives with no stable ground truth)

So we started building the missing piece.

Meet StatiBaker (SB)
Part of the ITIR suite (alongside TiRCorder, SensibLaw, etc.)
What is ITIR?
Intergenerational Trauma-informed Identity Rebuilder

StatiBaker is not a chatbot.
It’s not an agent.
It’s a state compiler.

It takes the things you already produce — and bakes them into a daily, inspectable, local-first state summary.

Think:

yesterday → what actually happened

today → what matters

what’s unresolved

what agents (if any) are allowed to do next

All traceable back to raw logs.
No hallucinated memory. No silent rewriting.

Why this exists (aka: why OpenClaw / Moltbook alone isn’t enough)
OpenClaw-style systems are great at:

automation

long-running agents

“doing stuff for you”

Moltbook-style experiments are great at:

agent-to-agent interaction

emergent narratives

stress-testing social AI dynamics

But they all struggle with one thing:

👉 Explaining what actually happened yesterday, in a way you can audit.

SB sits under agents, not above you.

It treats:

journals (text or voice)

TODOs

calendars

git commits

agent logs

smart home state

system failures

“I tried this and it broke”

…as first-class evidence, not vibes.

Key constraints (non-negotiable)
Local-first
Offline works. Cloud optional. No silent upload.

Append-only
Raw events are immutable. Derived summaries are recomputable.

Witness, not verdict
The system preserves and contextualises. It does not diagnose, judge, or optimise your life.

Expansion is always cheaper than summarisation
You can always drill back to source.

This is why it pairs naturally with:

TiRCorder (voice + narrative capture)

OpenRecall-class UIs (scrubbing raw time)

OpenClaw / Moltbook-style agents (who need a sane, non-mythologised state surface)

The mental model
Git + Time Machine + Morning Brief
Not “AI watching you”.
Not “AI inventing a story about you”.

What we’re looking for
Contributors who care about:

local-first AI

agent hygiene (permissions, auditability)

Linux / self-hosted workflows

timelines > chat logs

making AI boring in the right ways

Python, FastAPI, UI, infra, theory people welcome.

Repos & docs are public, early, and opinionated — discussion welcome.

If OpenClaw or Moltbook made you think:
“cool, but where’s the ground truth?”

…this is that layer.

About me:

I’m an open-source developer and systems tinkerer focused on local-first, inspectable tooling.

I maintain a number of self-hosted and local-compute–oriented projects, including TiRCorder and other ITIR-suite tools such as StatiBaker and SensibLaw, alongside ongoing experiments in voice capture, state tracking, and agent-adjacent infrastructure. Most of my work is built to run offline, on imperfect hardware, and with explicit auditability.

I’ve been active in the broader open-source and Linux community for years, including participation on the Linux Kernel Mailing List (LKML) around AMD GPU / ROCm regressions, particularly RX580 / gfx803 compute stability. A lot of my recent work has involved pushing deprecated or edge-case hardware back into usefulness through careful systems work rather than abstractions.

I began studying Computer Science in 2017 but didn’t complete the degree due to COVID-era housing instability. Since then, I’ve continued learning and contributing primarily through open source — maintaining ~30 public repositories and contributing thousands of commits across multiple projects.

Professionally, I’ve worked in software and systems roles across a range of industries, with an emphasis on real-world-stable infrastructure, not demos. I care deeply about agency-respecting systems, where users can inspect what happened, trace outputs back to inputs, and opt out of automation when needed.

My work tends to sit at the intersection of:

open, inspectable pipelines

long-form capture (voice and text)

self-hosted workflows

systems you can run, reason about, and audit locally

Happy to answer questions or dive deeper into any of the projects.

All the best!
FAQ:
1. “Is this watching me?”

No. Nothing is captured unless you explicitly enable a source; everything is local‑first and append‑only.

2. “What do I actually get day‑to‑day?”

A short daily brief you can read in under a minute, plus a drill‑down path back to raw logs.

3. “Is it telling me what to do?”

No. It’s a witness, not a verdict; it never diagnoses, judges, or optimizes you.

4. “Do I need agents/LLMs?”

No. Agents are optional; SB just compiles state from whatever you already produce.

5. “Is this a huge suite I have to learn?”

You can use any piece on its own — the suite only exists to share schema and timelines.

Suite Components:

- ITIR (Interpretive / Temporal Record)

Explicit interpretation layer over SensibLaw’s structural substrate; all ITIR objects are non-authoritative overlays with required SL TextSpan provenance. No interpretation without span backing.

References: docs/itir_model.md, docs/user_stories.md

- StatiBaker (SB)

Daily state distillation engine; append-only ingestion of human/system/environment streams; emits traceable daily brief + machine-readable state. No inference, no judgment, no optimization.

References: StatiBaker/README.md

- TiRCorder

Voice-activated capture + transcription pipeline; event/narrative capture layer aligned to shared schema; supports Whisper/cTranslate2 and remote WebUI.

References: tircorder-JOBBIE/README.md

- SensibLaw (SL)

Legal corpus ingestion + canonical graph layer; extracts rules and structures legal sources + stories into duties/harms/remedies graph. Deterministic ingest, versioned storage, receipts.

References: SensibLaw/README.md

- SL-reasoner

Interpretive scaffold for SL outputs; explicitly labeled hypotheses with disclaimers; read-only against core payloads.

References: SL-reasoner/README.md

- ITIR Ribbon

Timeline ribbon contract + lens DSL shared across ITIR/SB/SL; conserves named quantity under lenses, not narrative meaning.

References: itir-ribbon/README.md

———

Adjacent Submodules & Supporting Tools (Included in ITIR-suite)

- OpenRecall

Local-first “memory” UI via periodic screenshots + OCR; searchable timeline history. Good pairing as a raw time surface.

References: openrecall/README.md

- WhisperX-WebUI

Gradio UI for Whisper/WhisperX transcription with diarization and timestamps; supports multiple backends and VAD/UVR.

References: WhisperX-WebUI/README.md

- SimulStreaming

Real-time ASR + translation pipeline (Whisper + EuroLLM) with streaming policies and low-latency simulation.

References: SimulStreaming/README.md

- whisper_streaming

Earlier Whisper streaming implementation (now superseded by SimulStreaming); still useful as reference.

References: whisper_streaming/README.md

- chat-export-structurer

Local parser for ChatGPT/Claude/Grok exports into SQLite + FTS; streaming ingest for huge exports.

References: chat-export-structurer/README.md

- reverse-engineered-chatgpt

Unofficial ChatGPT web interface wrapper (session-token based).

References: reverse-engineered-chatgpt/README.md

- notebooklm-py

Unofficial NotebookLM API/CLI for bulk import, research automation, and artifact export.

References: notebooklm-py/README.md

- Chatistics

Chat log parsing to DataFrames; supports WhatsApp, Telegram, Messenger, Hangouts.

References: Chatistics/README.md

- pyThunderbird

Python access to Thunderbird mail; can be used for email ingestion pipelines.

References: pyThunderbird/README.md

Mods please note this project is not currently affiliated with any formal brand and instead represents a project for social good, in particular with the intent to reduce/avoid ensh*ttification and social harms. No funding exists at present.

Sorry, this post was removed by Reddit’s filters.

Upvote
0

Downvote

2
Go to comments

Share
u/tonkotsu-ai avatar
tonkotsu-ai
•
Promoted

Stop coding, start leading. Manage an entire team of coding agents from a doc. Try Tonkotsu - FREE.
Learn More
tonkotsu.ai
Thumbnail image: Stop coding, start leading. Manage an entire team of coding agents from a doc. Try Tonkotsu - FREE.
Join the conversation
Sort by:

Best

Search Comments
Expand comment search
Comments Section
u/TotalEmotional9530 avatar
TotalEmotional9530
OP
•
2d ago
Hi all! Please feel free to ask me any questions! I'm really seeking diverse inputs as I want this to be something that works for everyone.


Upvote
-1

Downvote

Reply

Share

52

u/TotalEmotional9530 avatar
TotalEmotional9530
OP
•
2d ago
Across a day you do a bunch of real work that often never makes it cleanly into a timesheet — short calls, half-written emails, notes to yourself like “missed filing X, do tomorrow”, etc. Most of that gets reconstructed from memory later, which is fragile.

StatiBaker sits under your existing tools and keeps an evidence-backed timeline of what actually happened (calendar events, drafts, calls, voice notes, command activity — only what you explicitly enable).

At the end of the day / next morning you get:

a factual “yesterday” view

a list of unresolved things that were mentioned but not finished

an optional draft activity summary you can review before copying into a timesheet or follow-up system

It doesn’t bill clients, prioritise tasks, or judge anything — it just gives you a reliable truth basis so you’re not reconstructing your week under stress. All local, auditable, and optional.


Upvote
1

Downvote

Reply

Share

27

Community Info Section
r/selfhosted
Join
Self-Hosted Alternatives to Popular Services
A place to share, discuss, discover, assist with, gain assistance for, and critique self-hosted alternatives to our favorite web apps, web services, and online tools.

Show more
Created Jul 8, 2014
Public
770K
Weekly visitors
11K
Self-Hosters
Community Bookmarks
Wiki
Discord / Matrix
r/selfhosted Rules
1
Spam / Low-Effort / Off-Topic
2
Self-Promotion / Affiliate Links
3
Hate-speech, Bullying, & Harassment
4
No Direct Ads for VPS/Hosting Services
5
Post Flair Is Mandatory
6
Blog Link Posts
7
Dashboard Posts / Wednesday Exceptions
8
AI, LLM's, "Vibe Coding", AI-Assisted Apps / ONLY ON FRIDAYS
9
All Reddit Rules Apply
10
Must Be About Self-Hosting
11
No Standalone Mobile Apps (Companion Apps Allowed)
Read This First!
👋🏼 Welcome to /r/SelfHosted!
Before you get started please read through this post! It contains a bunch of useful information so you can make the most of your time here.

We welcome posts that include suggestions for good self-hosted alternatives to popular online services, how they are better, or how they give back control of your data. Providing any hints and tips is greatly appreciated by our less technical readers!

For example:

Service: Dropbox - Alternative: Nextcloud
Service: Google Reader - Alternative: Tiny Tiny RSS
Service: Blogger - Alternative: WordPress
🧵 Important Threads
Google Photos Mega Thread
🔗 Important Links
The Official Wiki
What is Self-Hosting?
The Official Discord Server
The Official Matrix Server
🖥️ Related Subreddits
/r/HomeServer
/r/datahoarder
/r/musichoarder
/r/privacy
/r/Rad_Decentralization
/r/Syncthing
/r/Traefik
/r/WebApps
📄 Useful Lists
Awesome-Selfhosted List of Self-Hosted Software
Awesome-Sysadmin List of SysAdmin tools and Software
Awesome Docker Apps List of Docker-Enabled apps, tools, and software
🎧 Relevant Podcasts
The Selfhosted Podcast
Insight, information, and opinions
Relevant Interviews
Self-hosted tool debates
Moderators
Message Mods
u/kmisterk
KmisterK, Liberated.
u/astuffedtiger
u/adamshand avatar
u/adamshand
nz.adam
u/NikStalwart avatar
u/NikStalwart
u/alpay-on
u/usrdef
Opsec
u/FnnKnn
Orchomenos
u/LeftBus3319 avatar
u/LeftBus3319
u/Bjeaurn
u/nashosted 
chmod777
Noted
View all moderators
Reddit Rules
Privacy Policy
User Agreement
Accessibility
OSA Information
Reddit, Inc. © 2026. All rights reserved.

Collapse Navigation


