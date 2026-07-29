---
title: "Part 1: Why Post-Quantum Multi-Recipient Encryption?"
description: "I've spent decades building UIs. AI is about to evaporate them."
date: 2026-07-29
tags:
 - AIUI
 - generative UI
 - intent-based interfaces
 - human-computer interaction
 - information design
 - Edward Tufte
 - Stephen Few
 - human-centered AI
 - responsive design
 - conversational interfaces
 - software history
 - future of computing.

draft: false
---

# The Classic UI Is Dead. Long Live the AIUI.

*I’ve spent decades building UIs. AI is about to evaporate them.*

I have spent most of my career building user interfaces.

I built them for mainframes, minis, PDP-11s, control equipment, DOS, Atari, OS/2, Windows, the Lisa and classic Mac OS. I worked with vector displays, raster displays and RIPs. I wrote them in assembler, C, C++, FORTRAN, Java, Python and JavaScript—with AWT, Swing, Qt, HTML, jQuery, Svelte and LiveView.

Before the iPhone, I built mobile interfaces with BREW, J2ME, Psion and BlackBerry—and even created my own language, PhoneScript. Since then, I have built editors, debuggers, games, spreadsheets, trading systems, websites, chatbots and terminal interfaces.

Yes, I have really done it all.

And after all that machinery, every user interface reduces to a simple loop:

1. Render information and choices.
2. Accept input.
3. Render the response—updating the information and choices.

That is it. Windows, buttons, menus, forms, gestures, command lines and chat boxes are merely different implementations of this loop.

## From commands to intent

For decades, we implemented the loop by predicting every journey in advance. We designed screens, fields, dialogs and navigation trees, then encoded every permitted path through them.

That was enormously expensive. A new requirement meant new screens. A changed workflow meant redesign, implementation, testing, documentation, training and support. The interface gradually hardened around yesterday’s understanding of the work.

An AIUI reverses that relationship.

Instead of making a person translate an intention into our predetermined sequence of controls, the person states the desired outcome. The system determines the procedure, asks for missing information and renders whatever interface is useful at that moment.

Jakob Nielsen describes this as the move from command-based interaction to **intent-based outcome specification**. Google’s work on [generative UI](https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/) takes the idea further: the interface can be generated for a particular person, question and context instead of selected from a fixed collection of screens.

This idea is not entirely new.

Many forms could have been replaced years ago by adaptive questioning: a [dichotomous key](https://content.ces.ncsu.edu/identification-of-common-trees-of-north-carolina) that selects the next question from the previous answer, or an expert system such as Stanford’s [MYCIN](https://i.stanford.edu/pub/cstr/reports/cs/tr/82/926/CS-TR-82-926.pdf), which used rules to conduct a medical consultation.

What is new is that GenAI does not require us to anticipate and hand-code every branch.

We can model the data, capabilities, rules and permissions, then let the AI compose the interaction around the user’s goal. Maintenance moves away from screen choreography and toward domain models, tools, policies and guardrails.

The marginal cost of supporting a new path through the system falls dramatically.

Responsive design and platform porting also largely disappear as separate activities. We no longer need to handcraft and maintain different flows for desktop, mobile, tablet, terminal and control room. The same intent and domain model can be rendered appropriately for each device, available space and mode of interaction.

The classic UI is therefore dead—not because buttons and charts disappear, but because the **prebuilt screen is no longer the fundamental unit of software**.

## Beyond the rectangle

What are most of our supposedly modern interfaces?

Lists. Forms. Detail screens. Charts. Tables—occasionally editable.

They are still shaped by the keyboard and by the flat, two-dimensional territory of a mouse pointer or phone screen.

But that is not how people naturally express themselves. We communicate through speech, intonation, gaze, facial expression, gesture, posture and movement: three dimensions unfolding through time.

Research into multimodal interaction has pursued this idea for decades. Sharon Oviatt described systems combining speech, touch, gesture, gaze and body movement as early as 1999. More recent research continues to show how modalities such as [gaze and speech complement one another](https://eprints.gla.ac.uk/379718/): one establishes attention while the other expresses meaning.

The hardware is beginning to catch up. Apple Vision Pro is controlled through [eyes, hands and voice](https://www.apple.com/newsroom/2023/06/introducing-apple-vision-pro/). Meta’s display glasses combine cameras, audio, AI and an [EMG wristband that detects subtle muscle movements](https://about.fb.com/news/2025/09/meta-ray-ban-display-ai-glasses-emg-wristband/). Google’s Android XR allows Gemini to share the wearer’s viewpoint and understand the surrounding world.

These devices are no longer toys, but today’s headsets are unlikely to be the final answer. They are transitional machines—evidence that computing is escaping the rectangle and entering the same physical, visual and temporal world that we inhabit.

The future AIUI will not merely generate a better screen. It will see, listen, speak and respond to the whole person.

## Escaping the programmer’s aesthetic

GenAI can also free us from the banality of the programmer’s aesthetic.

We all recognize software whose implementation became its design: arbitrary panels, acres of wasted space, unreadable tables and dashboards filled with whichever widgets the framework happened to provide.

And pie charts—so many pie charts.

These interfaces expose database schemas, program structure and toolkit limitations. Users must adapt their thinking to the programmer’s model of the system.

Presentation software created a related disease: *death by PowerPoint*. Complex arguments are squeezed into bullets, templates and slide-sized fragments until the format determines what can be said.

Edward Tufte’s criticism was not simply that PowerPoint slides are ugly. It was that their [“cognitive style” can weaken technical reasoning](https://www.edwardtufte.com/notebook/the-columbia-evidence/) by suppressing detail, comparison and uncertainty precisely when they matter most.

The same thing happened to dashboards. The availability of a chart became the reason to use it. The container dictated the content.

Tufte, Stephen Few and others spent decades developing principles for communicating information clearly, densely and honestly. Most programmers never encountered that work. GenAI can draw on this accumulated knowledge every time it creates an interface.

It can determine what matters and select the representation that makes it most apparent: a sentence, dense table, chart, map, timeline, comparison, simulation or alert. It can remove decoration, expose uncertainty, emphasize an anomaly and use the available space intelligently.

It can often make these choices better than a human designer working months earlier, forced to predict an unknown user in an unknown situation.

The interface is no longer a fixed container into which information must be forced. It becomes a contextual rendering of what matters now.

## What we may lose

A fixed interface is rigid, but its rigidity has value.

It is stable. People develop spatial memory and mastery. A button remains where it was yesterday. Two colleagues can look at the same screen. Instructions can say exactly what to click. Actions are enumerable, testable and auditable.

An AIUI may instead be probabilistic, personal and ephemeral. It can hide possibilities the user did not know to request. It can misunderstand intent, invent an inappropriate representation or perform several consequential actions behind one innocent sentence.

Personalization can eliminate the shared surface on which teaching, collaboration and accountability depend.

We may also lose craft. A carefully designed tool embodies accumulated knowledge about its domain. Replacing it with an endless conversation can make expert work slower, less precise and less satisfying.

Ben Shneiderman’s [human-centered AI](https://academic.oup.com/book/41126) offers the necessary correction: high automation need not mean low human control. The best systems should be comprehensible, predictable, reversible and trustworthy.

## The interface after the interface

The future is not a blank chat box.

It is a fluid collaboration in which language expresses intent, AI assembles the path, and visual, audible or tactile controls appear whenever they are the clearest way to understand, decide or act.

Conversation, direct manipulation, generated displays and physical expression will coexist.

We will still design—but at a different level.

We will design the vocabulary of possible actions, the truthfulness of representations, the boundaries of authority, the visibility of state and the routes back from error. We will design how the system earns trust.

After forty years of constructing screens, I find the conclusion both liberating and uncomfortable:

The UI was never the product. It was the scaffolding between human intention and computational capability.

AI can remove much of that scaffolding.

Our job is to make sure it does not remove the human with it.


