# /voice

Record and transcribe voice notes using AI transcription.

## When to Use

- Capturing thoughts while walking/commuting
- Recording meeting notes hands-free
- User says "voice note", "record", "transcribe"

## Instructions

### Prerequisites

Voice transcription requires one of:
1. **OpenAI Whisper API** - Set `OPENAI_API_KEY` environment variable
2. **Local Whisper** - Install `whisper` CLI (`pip install openai-whisper`)
3. **macOS Dictation** - Built-in, no setup required

### Option 1: Quick Voice Note (macOS)

For quick capture using macOS dictation:

1. Tell user to press `Fn Fn` (double-tap Function key) to start dictation
2. Speak their note
3. Press `Fn` again to stop
4. Paste the text and create a note from it

### Option 2: Record and Transcribe

If user wants to record audio file:

1. **Record audio**
   ```bash
   # macOS - record 60 seconds
   rec recording.wav trim 0 60
   
   # Or use QuickTime/Voice Memos
   ```

2. **Transcribe with Whisper**
   ```bash
   # Using OpenAI API
   curl https://api.openai.com/v1/audio/transcriptions \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     -F file="@recording.wav" \
     -F model="whisper-1"
   
   # Or local Whisper
   whisper recording.wav --model base --output_format txt
   ```

3. **Create note from transcript**
   - Ask user for note type (Note, Meeting, Daily)
   - Create note with transcript as content
   - Add timestamp and duration metadata

### Option 3: Live Transcription (Advanced)

For meeting transcription:

1. Use a transcription service that outputs text in real-time
2. Pipe output to a temporary file
3. When done, create Meeting note with full transcript

### Skill Flow

```
User: /voice

Claude: Ready to capture a voice note. Choose your method:

1. **Quick dictation** - Press Fn twice to start macOS dictation, speak, then paste here
2. **Record file** - I'll guide you through recording and transcribing an audio file
3. **Meeting mode** - Set up live transcription for a meeting

Which would you like?
```

### Output Format

Create note with:
```yaml
---
type: Note  # or Meeting
title: Voice Note - {{timestamp}}
created: {{date}}
tags: [voice-note]
source: voice-transcription
duration: {{duration}}
---

# Voice Note - {{timestamp}}

## Transcript

{{transcribed_text}}

## Key Points

_Review and add key points from the transcript_

## Action Items

- [ ] _Extract any action items_

## Related

_Add links to related notes_
```

### Tips

- Voice notes work best in quiet environments
- Speak clearly and at moderate pace
- Review and edit transcripts - AI isn't perfect
- Extract key points and action items after transcription
- Link voice notes to relevant projects or people

### Environment Variables

```bash
# For OpenAI Whisper API
export OPENAI_API_KEY="your-key-here"

# For local Whisper, just install:
pip install openai-whisper
```

### Troubleshooting

- **No audio input**: Check microphone permissions in System Preferences
- **Poor transcription**: Try a quieter environment or speak more clearly
- **API errors**: Verify API key and check usage limits
