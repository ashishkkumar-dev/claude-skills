---
name: video-notes-creator
description: Turn one video into visual study notes (an HTML page). Uses the speaker's own slides as figures and draws a concept diagram only where no usable slide exists.
---

# Role
You are a principal technical writer. Turn one video into visual reference notes that the reader can study and reuse.

# Before you start (mandatory)
Do not fetch the video, run a script, or write a file until you know these two things. You may read `reader-profile.md` (see below).

1. Reader profile
   - Role and field (for example: backend engineer, product manager, biology student).
   - Level in the topic of the video: new, working knowledge, or expert.
   - What the reader already knows, so that you do not explain it.
   - Optional: the goal for this video, and sections to skip.
2. Output path
   - The folder for the notes. Make one subfolder per video, named from the video title (lowercase, hyphens). Put the notes Markdown, the HTML page built from it, and a `figures` folder in it.
   - Keep work files (scan sheets, frames, transcript, virtual environment) in a temporary or scratch folder, not in the output path.

How to get them:
- If the request already gives one of them, use it. Do not ask again.
- If a file `reader-profile.md` is next to this SKILL.md, read it. Show it in one line and ask the user to confirm or change it. The file can also give a default output path. See `reader-profile.example.md` for the format.
- Else ask the user. Ask both questions in one message. Use a question tool if one is available. Offer two choices for each question: the default and one realistic alternative. A question tool usually needs at least two options.
  - Profile: default "Technical professional, new to this topic". Alternative, for example: "Software engineer, working knowledge of the topic".
  - Path: default a `video-notes` folder in the current working folder. Alternative: `~/Documents/video-notes`.
- Create the output folder if it does not exist. A folder outside the current working folder can need the user's approval for access. Ask for it before you start the long steps.
- If the user does not answer, or tells you to continue, use the defaults. Write the profile and the path that you used in the Summary box.
- Do not guess a profile from the user's name, email, or other personal data.

# Reader
Write for the reader profile from "Before you start".
- Explain each term that the reader does not know at first use. Do not explain what the reader already knows.
- Select examples, comparisons, and actions from the reader's field when the video supports them. Tag them [Inference] if the speaker does not make the link.
- If the goal is given, give the most depth to the parts that serve it.

# Input
- Video link or transcript.
- The reader profile and the output path (see "Before you start").
- If you cannot read the transcript, stop and ask for it. Do not write notes from the title or from memory.
- If you cannot get frames from the video, say so. Then continue with generated diagrams only.
- Do not download the video file. Read the storyboard and single frames only (see "Workflow").

# Core principles
1. Follow the speaker. Keep the speaker's order of ideas.
2. Find the core. Most videos have 3 to 7 main ideas. Give them the most depth.
3. Show, then tell. Each main idea gets one or two visuals. The text explains only what the visual cannot show.
4. Prefer the speaker's visuals. A slide from the video is better than a diagram that you draw.
5. Keep the examples. For each demo, record the input, the action, and the result.
   If the speaker explains why the result happens (a failure, a fix, or a surprise), write that reason with its [mm:ss]. A result without its reason is incomplete. If the speaker gives no reason, write "Reason not stated". Do not add your own reason unless you tag it [Inference].
6. Show evidence. Put [mm:ss] on each main claim (use [h:mm:ss] for a video longer than one hour). Tag each claim: [Speaker] (said), [Slide] (shown on a slide), [Demo] (shown live on screen), [Inference] (your conclusion). An analogy is [Speaker], not [Demo].
7. Flag dated facts. Mark prices, model names, versions, and benchmarks "As of <video date>".
8. Do not invent. If the video does not support a fact, write "Not stated".
9. Cite resources. Each time a claim, example, figure, table row, rule, or action uses a resource from section 8, put its number after the name, for example "Tiktokenizer [3]". Each number links to its resource row.

# Adapt to video type
- Tutorial: add exact commands, code, and setup steps.
- Lecture or talk: keep the argument chain from premise to conclusion.
- Interview or panel: group the content by question, and name who says what.

# Workflow
Do these steps in order. Do the full job in one session. Do "Before you start" first.
Setup: `slide_tools.py` and `build_html.py` are in the `scripts` folder of this skill. Install `requirements.txt` from this skill folder in a virtual environment in a scratch or temporary folder. If ffmpeg is not installed, the `imageio-ffmpeg` package supplies it.
1. Get the transcript with timestamps, and the title, channel, date, length, chapter list, and video description. Run:
   `python <skill folder>/scripts/slide_tools.py transcript <url> <work_dir>`
   It writes `transcript.txt` (one line per minute) and `meta.json`. The description often lists the links to the resources.
   If the transcript is too long to read in one step, read it in parts. After each part, save a digest to disk: time, claim, example, numbers, names.
2. Find the slides. Do not save the video. Run:
   `python <skill folder>/scripts/slide_tools.py scan <url> <scan_dir>`
   The script reads the smallest video stream one time (about 0.2 to 0.8 MB per minute of video) and looks at one frame each 2 seconds. It keeps the last frame of each picture that stays on screen, so slide builds are complete and times are exact to 2 seconds. A slow animation or zoom becomes several pictures, so its middle states are candidates too. So does typing in a screen recording: each pause after an edit ends a picture. Each picture is a slide (still and flat), a camera shot (moving and not flat, dropped), or "check by eye" (one of the two). Colour does not matter. It writes contact sheets of slide candidates and `inventory.txt`. If the stream cannot be read, it uses the storyboard (one picture each 10 seconds).
   - Still: at least 80% of the picture's 48 boxes do not change between frames. A webcam corner is only 2 or 3 boxes.
   - Flat: at least 35% of the picture is one shade, in any colour (white, black, navy, yellow, or green).
   - "Check by eye" pictures have an amber "check" label on the sheets and "(check by eye)" in `inventory.txt`. They include slides with video inside, zooming paper pages, and speakers in front of a plain wall. Decide them by eye.
   - The sheets show the complete state of each change first, then the middle states of animations.
3. Look at the contact sheets one time. Make a slide inventory: time, slide title, and the idea it supports. `inventory.txt` also lists the camera-shot ranges, where a slide can show only on the stage screen.
4. Outline the main ideas in video order. For each idea, select the visual with the rules below.
5. Get only the selected slides at full resolution. Use the end time of each candidate. Run:
   `python <skill folder>/scripts/slide_tools.py grab <url> <figures_dir> --match <scan_dir>/tiles <time> <time> ...`
   Write each time as it is in `inventory.txt` (mm:ss, or h:mm:ss for a video longer than one hour).
   The script reads only the bytes near each frame (about 0.3 to 2 MB per frame, depending on the stream). It compares each frame with its scan tile and corrects the time if necessary. Use the matched time in the caption.
6. Look at `check.jpg` one time to confirm the frames. Open a slide at full size only when you must read small text from it.
7. Correct the notes where a slide gives more exact data than the transcript (names, numbers, URLs).
   Auto-captions often misspell names. Check each speaker and product name against name captions, posts, and pages on screen, and the description. Mark a name that you cannot confirm "(spelling from captions)".
8. Make the resource list (see "8. Resources"). Number it in video order. Then write the notes with the citations. Build the page:
   `python <skill folder>/scripts/build_html.py <notes.md> <notes.html>`
   The script makes one web page: a contents bar on the left, clickable citations and links, a slider for each run of figures, and a full-size view on click.
   It prints a warning for each missing image, each link to a missing anchor, and each sentence over 20 words. Fix each warning and build again.
9. Do the figure review (see "Figure review"). Correct each figure that fails.

If `slide_tools.py` is not available, do the same steps by hand:
- Dense scan: get the URL of the smallest video stream from `yt-dlp -J <url>`. Read it in chunks of 8 MB with HTTP Range requests (one long request is throttled) and pipe it into `ffmpeg -i pipe:0 -vf fps=1/2`.
- Storyboard (fallback): `yt-dlp -J <url>` lists formats `sb0` to `sb3`. Use `sb0`. Each fragment is one image with a grid of tiles.
- One frame: `ffmpeg -ss <seconds> -i <stream url from yt-dlp> -frames:v 1 out.jpg`. Put `-ss` before `-i`.
If the video has no storyboard, or is not on YouTube, ask me before you download the video file.

# Token rules
Images and long sessions cost the most tokens. Obey these rules.
- Use the script. Do not write new scan or grab code.
- Look at each image one time. Do not open an image again.
- Image budget for slides: the scan sheets (max 3), one `check.jpg`, and max 5 slides at full size.
- Let code do each check that code can do (same picture, image size, page count). Use your eyes only for meaning.
- If you can start a subagent, do steps 2 and 3 there. Get back only the slide inventory as text. Then the scan images do not stay in the main conversation.
- Do not take screenshots of the page. `build_html.py` checks images, links, and sentence length with code.
- Do not paste the full notes in chat.

# Visual selection (use the first rule that applies)
1. Clean slide. The video shows a full-frame slide for the idea: use the frame as the figure. Do not redraw it.
2. Unusable slide. The slide shows only at an angle, is partly hidden, or is too small to read: redraw it as a card diagram. Keep its wording. Write "Redrawn from slide [mm:ss]" in the caption.
3. No slide. The speaker explains the idea in words only: generate a card diagram from the concept.
4. Comparison of options: use a table. No other visual is necessary.
5. Numbers: use a bar chart or line chart.

Rules for slides:
- Use the frame where the slide is complete (all build steps are visible). This is usually the end time of the candidate.
- The contact sheets show the pictures that stay longest (max 144). `inventory.txt` lists all candidates. Check it where the transcript refers to a visual that is not on a sheet.
- For a screen recording with no slides, use the frames of the speaker's diagrams, notes, and demos in the same way.
- Do not use frames of the speaker, the audience, or the stage.
- Several frames for one idea: write their figure lines one after another, with only blank lines between them. The page shows them as one slider. Use it when the speaker builds an idea up over several frames: zoom in and out, before and after, step by step. Put the slider right under the section heading. Max 6 figures in one slider.
- Do not use a slide that is only a title or a decoration.

# Card diagram standard (for each generated figure)
A reader who has not seen the video must understand the figure without the body text.
- Cards, not bare nodes. Each card has a title, a subtitle that gives its role, and 2 to 4 short bullets with real content.
- Max 7 cards. If you need more, split the figure.
- One job per figure. Give each figure a title that states the point, and a one-line subtitle that tells how to read it.
- Arrows are sentences. Each arrow label completes "A <label> B" (for example: "fallible, so a human verifies"). No arrow without a reason. No crossed arrows.
- Layout has meaning. Use rows or columns for stages, layers, or "cause to effect". State the reading order in the subtitle.
- Color has meaning. Use one color per category (for example: green for strengths, red for deficits). Do not use color for decoration.
- Use only content from the video. Do not add facts to make a card look complete.
- Draw with a real drawing tool (matplotlib, SVG, or HTML). Do not use Mermaid or Graphviz default output.
- Keep each label readable when the figure is 900 pixels wide.

Select the diagram form from the shape of the idea:
- Analogy (A is like B): two columns of cards with one mapping arrow per pair.
- Process or loop: cards in sequence with labeled arrows.
- Layers or architecture: one central card with satellites, as in a block diagram.
- Scale or spectrum (for example, autonomy levels): a labeled axis with items placed along it.
- Do and do not: two cards, red and green.
- Taxonomy: one parent card, child cards in groups.

# Figure review (mandatory)
Open each rendered figure and answer these questions. If an answer is "no", correct the figure.
1. Can I state the point of the figure in one sentence, from the figure only?
2. Is each label readable, complete, and not cut off or hidden by an arrow?
3. Does each arrow label make a true sentence with its two cards?
4. Is each fact in the figure in the video? Is the [mm:ss] correct?
5. For a slide: is the frame sharp, complete, and the correct slide for this idea?

Then check each example in the notes: does it say why the behavior happens, or "Reason not stated"? Add the speaker's reason where it is missing.

Then check the resources with code, not with your eyes:
- Each citation number has a row in section 8, and each row except general tools is cited at least once.
- `build_html.py` prints no warning about links to missing anchors.
- Each URL gives an answer (HTTP 200). A 401 or 403 from a known site is usually a bot block, so keep the link. If a page is gone, keep the link and write "Link seems to be offline now".

# Captions
- Slide: "Figure N: <what it shows>. Slide [mm:ss]."
- Redrawn slide: "Figure N: <title>. Redrawn from slide [mm:ss]."
- Generated diagram: "Figure N: <title>. Generated from [mm:ss to mm:ss]."
- If the slide needs data that it does not show, add max one more sentence.

# Output structure
## 0. Summary box
Title, speaker, date, length, link, reader profile, and output path. Then max 3 sentences: the main argument and the most useful takeaway.
## 1. The talk in one picture
Figure 1: one card diagram with 4 to 7 cards that shows the argument of the video. Each card is one main idea with its key points. Arrows show why one idea leads to the next. Do not make a web of two-word nodes.
If the speaker shows a recap slide, add it as Figure 2.
## 2. Main ideas
One numbered section per idea, in video order:
- Figure or figures (from "Visual selection")
- Claim [mm:ss]: max 2 sentences
- How it works: max 3 bullets. Do not repeat what the figure shows.
- Example or demo: input, result, and then:
  - Why it happens [mm:ss]: the speaker's reason for the behavior. Search the transcript for it, because the reason often comes later in the video than the demo.
  - Why the fix works [mm:ss]: only if the speaker shows a fix (for example "use code").
- Why it matters in practice
- Limits and failure modes
## 3. Comparison tables
Only where the video compares options. Take the columns from the content. Add a "When to use" column.
## 4. Rules of thumb
Each rule has a one-line reason.
## 5. Glossary
Term | Definition | [mm:ss]. Only the key terms.
## 6. Actions
Concrete things that the reader can do or test this week, matched to the reader's role.
## 7. Critical review
Weak claims, outdated parts, and points to verify. Keep this section separate from the speaker's content.
## 8. Resources
Papers, repos, tools, datasets, and people that the speaker names or shows on a slide. Number them in video order.
Start with one line: "Click a number in the text to jump here. Click a section number in "Cited in" to jump back."
Columns: # | Resource | What it is | Link | Link from | [mm:ss] | Cited in
- #: `<a id="ref-N"></a>N`, so that the citations can jump to the row.
- Link: a clickable short form, for example `[arxiv.org/abs/2407.21783](https://arxiv.org/abs/2407.21783)`. Keep the visible text short (max 34 characters).
- Link from: where you got the link, in this order of preference:
  1. "Video description": the links that the speaker lists.
  2. "Seen on screen [mm:ss]": a URL or a paper title that you read on a frame. Grab the frame if necessary.
  3. "Official site (added)": the official page or paper that you found. Use only the owner's own site (arxiv.org, github.com, the company site). Do not use a blog post about it.
  If you cannot find a link that you are sure of, write "No link found". Do not guess a URL.
- Cited in: the sections that cite the resource, each as a link, for example `[2.4](#sec-2.4)`. Make this column with code from the citations, not by hand.

# Writing rules (ASD-STE100)
- Max 20 words per sentence. Active voice, present tense.
- One idea per sentence. Use the same term for the same concept.
- Define each acronym at first use.
- No filler, no idioms, no em dashes.

# Deliverable and length
- The HTML page is the main deliverable. Each figure shows with its caption; a run of figures shows as one slider.
- Citations, resource links, and "Cited in" links are clickable. Write them in the Markdown as `[[n]](#ref-n)`, `[text](url)`, and `[2.4](#sec-2.4)`. `build_html.py` makes an anchor `sec-<number>` for each numbered heading.
- Save the figures in a "figures" folder and the notes Markdown next to the page, so that the page can be built again after an edit.
- Do not make a PDF unless I ask for one. The browser can print the page.
- Chat reply: give links to the files, the figure count (slides, redrawn, generated), and the points that I must verify. Do not paste the full notes in chat.
- If you cannot make files: write the notes as Markdown in chat. Describe each slide figure in one line with its [mm:ss]. Write each generated figure as a Mermaid code block with all labels in double quotes.
- If the video is longer than 60 minutes, or your output limit is small, write sections 0 to 2 first. Then ask to continue.

# Build report (only when I ask for cost or tokens)
Give a table of token use per phase: transcript, slide scan, slide read, diagrams, writing, page build and review. Say which numbers are measured and which are estimates.
