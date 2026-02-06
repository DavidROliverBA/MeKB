# Building MeKB: A Personal Knowledge Base That Actually Works

You know that decision you made six months ago? The one your colleague is now asking about? You *know* you wrote it down. You can picture the meeting. You remember the whiteboard. But where is the note?

Maybe it's in Notion. Or was it a Google Doc? A Confluence page someone shared? An email thread? A Slack message you starred?

This is the problem I kept running into. Not a lack of notes — I had thousands. The problem was that my knowledge was scattered across fifteen different apps, none of which talked to each other, and all of which would happily hold my data hostage if I ever wanted to leave.

So I built something different.

## The question that started it all

What if your notes could grow smarter over time, instead of just piling up?

Most note-taking apps are glorified filing cabinets. You put things in, and if you remember exactly where you put them, you can get them out again. But knowledge isn't filing. Knowledge is about connections — the relationship between that decision you made in January and the problem you're solving in June.

I wanted a system where writing a note today would make all my past notes more valuable. Where linking two ideas would create a path that I, or an AI assistant, could follow later.

## What MeKB actually is

Plain text files. That's genuinely it.

MeKB is a collection of Markdown files — the same format that READMEs, Wikipedia edits, and half the internet already use. You can open them in anything: Notepad, VS Code, Obsidian, your phone's text editor. They'll still be readable in twenty years.

The simple trick is that every note has a *type*. A meeting note knows it's a meeting. A concept knows it's a concept. A person note knows it's about a person. This tiny bit of structure — just a few lines at the top of each file — lets you ask questions across your entire knowledge base:

*"Show me all decisions from last quarter."*
*"Who did I last meet with about the API project?"*
*"What concepts am I tracking that I haven't reviewed in three months?"*

You don't need any special software to write the notes. The structure makes them queryable, but they're perfectly readable without it.

## Three principles I won't compromise on

**1. Knowledge outlives tools.**

Notion might not exist in ten years. Evernote nearly didn't. Google has killed more products than most companies have launched. But a text file from 1990? Still opens fine.

Your notes are the valuable thing. The app is just a window. MeKB files have zero lock-in, zero subscription, and zero risk of a "we're sunsetting this product" email destroying years of work.

**2. Collaboration is sharing a folder.**

Want someone to contribute to your knowledge base? Share the folder. Git, Dropbox, a USB stick — whatever works. No accounts to create, no permissions to configure, no "you need a paid seat" conversations.

**3. Your data deserves protection.**

Not everything should be searchable by everything. MeKB has a simple classification system: public, personal, confidential, secret. Mark a note as confidential and it won't show up in search results, AI queries, or exports. It's still just a text file you own — it's just a file that knows it should be careful about who sees it.

## Why plain text wins

I could have built this on a database. It would have been faster to query. But it would have introduced a dependency — something that could break, something you'd need to install, something between you and your notes.

Plain text means:
- **Zero setup** — clone the folder, start writing
- **Universal compatibility** — any editor, any operating system, any device
- **Version control** — Git tracks every change you've ever made
- **Grep-able** — the entire Unix toolkit works on your notes out of the box
- **Future-proof** — text files from the 1970s are still readable today

The trade-off is speed. Searching ten thousand text files with grep takes a few seconds. So I built a search index — a small script that creates a lookup table. Now searches take 0.01 seconds. But if the index breaks, you still have grep. Your notes never depend on the tooling.

## The magic: connections

Here's where it gets interesting.

When you write `[[Person - Jane Smith]]` in a meeting note, you've created a link. Jane's note now knows it's referenced from that meeting. The meeting knows Jane was there. Follow the links and you can see every meeting Jane attended, every decision she was part of, every project she's connected to.

This isn't a feature I built. It's just how wiki-links work in Markdown. The files reference each other by name, and any tool that understands double-bracket links (Obsidian, Foam, Logseq) will show you the connections.

But it's the AI part that surprised me. When you give a language model access to a well-linked knowledge base, it can traverse those connections. Ask it "what do we know about the API strategy?" and it doesn't just search for those words — it follows the links from the API decision to the meeting where it was discussed, to the people who were there, to the project it relates to. Context that would take you twenty minutes to reconstruct takes two seconds.

Knowledge compounds like interest. Every note you add makes every existing note slightly more valuable, because there's one more thing it might connect to.

## What I built on top

The plain text files are the foundation. On top of them, I built 36 AI skills — small instruction sets that automate common tasks:

- Type `/daily` and your day is structured with a journal template
- Type `/meeting Sprint Planning` and you get a meeting note pre-linked to the right project
- Type `/stale` and you see which notes haven't been reviewed in months
- Type `/q machine learning` and you search by meaning, not just keywords

These skills work with Claude Code, but they're just Markdown instruction files. You could read them and follow the steps manually. The AI is a convenience, not a requirement.

I also built 12 Python scripts for the heavy lifting: search indexing, a knowledge graph builder, a static site generator, notifications, scheduled maintenance. They all run on Python's standard library — no packages to install. Clone the repo and they work.

And because I believe in testing the things I ship, there are 236 tests covering all of it. A CI pipeline runs them automatically on every change. The whole suite takes less than a third of a second.

## A day in the life

Here's what using MeKB actually looks like.

Morning. I run `/daily` and get today's journal page. It pulls in any tasks due today, any meetings on the calendar, and a note I wrote three weeks ago that's due for review.

10am. Sprint planning. I run `/meeting Sprint Planning` and get a note linked to the project, with space for attendees, decisions, and action items. During the meeting, I write in plain text. Links to people and systems create the connections automatically.

2pm. Someone asks about a decision from November. I run `/q API authentication` and get the decision note, the meeting where we discussed it, and the concept note explaining our authentication pattern. All connected by links I wrote at the time.

4pm. I'm reading about a new approach to data pipelines. I run `/concept Event Sourcing` and capture what I've learned. I link it to the two projects where it might be relevant. Those projects now know about event sourcing. Next time someone asks about either project, this concept will surface.

Friday. I run `/stale` to catch notes going stale. Three concept notes haven't been reviewed in four months. I spend fifteen minutes updating them with what I've learned since. The knowledge base gets healthier, not just bigger.

## What I got wrong

Plenty.

**Over-engineering.** I built dashboards with fancy Dataview queries before I had enough notes to make them useful. I created automation for problems I didn't have yet. The lesson: start with notes, add structure when you feel the pain.

**Too many categories.** My first version had twenty note types. Nobody needs twenty types. MeKB has eleven, and honestly you could get by with five: Daily, Note, Task, Person, Meeting. Add the rest when you need them.

**Not enough linking.** For the first month, I wrote notes but rarely linked them. The knowledge graph was a collection of islands. Now I link aggressively — if I mention something, I link it. The upfront cost is two square brackets. The long-term value is enormous.

**Premature optimisation.** I spent days on a vector embedding system before I had enough notes for it to matter. Simple keyword search works brilliantly for the first thousand notes. Save the fancy stuff for later.

## Try it

MeKB is free, open source, and yours to modify.

1. Fork the repo
2. Open it in Obsidian (or any text editor)
3. Run `/start` for guided setup, or just open `Note - Welcome to MeKB.md`
4. Start writing

There's no account to create, nothing to install (unless you want the Python scripts), and no subscription. If you decide it's not for you, you've lost nothing — they're just text files, and they're already on your machine.

The goal isn't to build the perfect knowledge system. It's to build *your* knowledge system — one that grows with you, belongs to you, and will still work long after the current crop of note-taking apps has come and gone.

Start simple. Link liberally. Let knowledge compound.

---

*MeKB is open source under the MIT licence. Find it at [github.com/DavidROliverBA/MeKB](https://github.com/DavidROliverBA/MeKB).*
