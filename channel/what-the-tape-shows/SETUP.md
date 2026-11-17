# What The Tape Shows: channel setup

**Name:** What The Tape Shows · **Handle:** @WhatTheTapeShows (unused when checked on 2026-10-15; claim it soon)
**Format:** AI-narrated commentary Shorts on viral internet stories. Both sides, then what the footage actually proves.
**Assets in this folder:** `profile-picture-800.png`, `banner-2560x1440.png`, `watermark-150.png`

---

## 1. Create the channel (you do this; I can't create accounts or sign in)
1. Sign in to YouTube with the Google account you want to own the channel.
2. Profile picture → **Settings → Create a new channel** (or **Add or manage your channels → Create a channel**).
   This makes a separate **Brand Account** channel, so it stays apart from your personal or other channels and you can add managers later.
3. Name: `What The Tape Shows`. Handle: `@WhatTheTapeShows`.
4. Go to **youtube.com/verify** and verify by phone. This unlocks custom thumbnails, uploads over 15 min, live streaming, and appeals of Content ID claims.
5. Turn on **2-Step Verification** for the Google account. Commentary channels attract hijack attempts and "copyright" phishing emails.

## 2. Branding (YouTube Studio → Customization → Branding)
| Slot | File | Notes |
|---|---|---|
| Picture | `profile-picture-800.png` | Shown as a circle. Everything is inside the circle |
| Banner | `banner-2560x1440.png` | All text is inside the 1546×423 area every device shows |
| Video watermark | `watermark-150.png` | Display time: **Entire video**. Placement is automatic; the Shorts feed doesn't show it, but long videos and Shorts on desktop do |

## 3. Basic info (Customization → Basic info)
**Description** (paste):
> Viral story? We check the tape.
>
> What The Tape Shows breaks down the internet's biggest moments in under two minutes: what each side says, what the footage actually proves, and what it doesn't. Every Short shows the sources on screen and links them in the description.
>
> Narration is an AI voice; the research, script and opinions are ours. Opinions are marked as opinions.
>
> New Shorts every week. Tell us which story we should check next.

**Links:** none needed to start. **Contact email:** use a separate inbox for the channel (sponsors, copyright notices), not your work email.
**Keywords** (Settings → Channel → Basic info): `commentary, internet drama, viral stories, explained, shorts, news commentary, drama explained`
**Country:** your country of residence (affects monetization terms and tax info).

## 4. Upload defaults (Settings → Upload defaults)
- **Title:** leave blank (each Short gets its own, from `youtube-metadata.md`)
- **Description template:**
  ```
  <one-line summary>

  Was <question>? Tell me in the comments.

  Sources (clips used for commentary and criticism):
  <sources>

  Music:
  <music credit from commentary-kit/music/CREDITS.txt>

  Narration: AI voice. Script, research and opinions: What The Tape Shows.
  #shorts #commentary
  ```
- **Visibility:** Private (publish only after you've watched the final file)
- **Category:** Entertainment (News & Politics can put your Shorts next to news info panels and gets stricter treatment)
- **Language:** English · **Caption certification:** none · **Comments:** "Hold potentially inappropriate comments for review"
- **Audience:** "No, it's not made for kids" (set it per video too)
- **Altered or synthetic content:** leave it **off** by default. The footage is real and the narrator is a generic AI voice that
  doesn't imitate anyone, which YouTube's guidance says doesn't need the label. Turning it on could wrongly suggest the *clips* are fake.
  Turn it **on** for any video that uses a voice imitating a real person, or AI-generated realistic images or video.

## 5. Monetization: the real risk is "inauthentic content", not the numbers
**Thresholds** (2026, per secondary sources; confirm on YouTube's YPP page before applying):
- Tier 1 (fan funding, Shopping): 500 subs + 3 uploads in 90 days + **3M Shorts views in 90 days**
- Tier 2 (Shorts ad revenue share): 1,000 subs + **10M Shorts views in 90 days**
- Reported (not confirmed): thresholds double for new applicants from **Feb 1, 2027** (1,000 subs + 20M Shorts views)

**YouTube's "inauthentic content" policy** (renamed from "repetitious content" in July 2025) targets mass-produced,
template-like videos, especially AI voice over reused clips. In January 2026 YouTube terminated channels for this. To stay clear:
1. **The "MY TAKE" section is mandatory in every Short.** Original analysis, not a recap. Reviewers check this first.
2. Keep third-party clips short (2–6 s each, one soundbite ≤10 s), always with narration over them. Never just a compilation.
3. Vary each Short: different music, hook style, graphics and pop-ups. Don't let 20 Shorts look identical apart from the topic.
4. Never read an article aloud. Write your own script from several sources (the skill does this).
5. Post at a human pace (3–5 per week), not dozens a day.
6. Mention the AI narrator honestly (channel description + description template above).

## 6. Copyright plan
- Each Short's `licensing-manifest.md` (in `output-commentary/<slug>/`) lists every clip, its length on screen, and why it's used.
- **Content ID claim** (monetization goes to the claimant, the video stays up): dispute it as commentary/criticism, citing the
  manifest, or trim the claimed shot and re-upload.
- **Copyright strike** (a takedown notice): don't ignore it. A counter-notice is a legal statement, so only file one if you're confident.
  3 strikes = channel deleted. If in doubt, let the video go and change the sourcing.
- Avoid clips from sources known for aggressive claims, and never use music from the clips.

## 7. Posting playbook
- **Speed:** post within 24–48 h of a story breaking. Commentary Shorts on stale stories get few views.
- **Cadence:** 3–5 Shorts/week. On this PC one Short takes about 1.5–2 h of mostly unattended processing (`/commentary-short`).
- **Before publishing:** watch the file once with sound, set the title, paste the description, pin a comment with the
  question from the ending, choose the cover frame (or upload `thumbnail.png` where the app allows).
- **First week:** reply to every comment in the first hour after posting. It's the cheapest growth lever a new channel has.

## 8. What to track (YouTube Studio → Analytics → each Short)
| Metric | Healthy for a new Shorts channel | If it's low |
|---|---|---|
| Viewed vs. swiped away | 60%+ viewed | The hook (first 2 s) isn't landing: start on the most striking frame and number |
| Average % viewed | 70%+ (looping counts above 100%) | Cut the middle; it's too long for the story |
| Subscribers per 1k views | 1+ | The ending needs a stronger "why follow" (the series, the question) |

Use only Studio numbers; per-video views count every replay since March 2025, so views alone overstate how a Short did.

## 9. First steps checklist
- [ ] Create the channel + claim @WhatTheTapeShows
- [ ] Phone-verify + 2-Step Verification
- [ ] Upload picture, banner, watermark
- [ ] Paste the description and keywords; set the upload defaults
- [ ] Upload the first Short (`output-commentary/kelly-clarkson-molly/`) as **Private**, watch it on your phone, then publish
- [ ] Run `/commentary-short` for Short #2 within the next day or two
