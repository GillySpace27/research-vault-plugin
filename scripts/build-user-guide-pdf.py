#!/usr/bin/env python3
"""Build the companion PDF of USER-GUIDE.md (the markdown is the source of
truth; this renders a print/email-friendly version with native diagrams).

    pip install reportlab
    python scripts/build-user-guide-pdf.py [output.pdf]   # defaults to ./USER-GUIDE.pdf
"""
import html, os, sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted,
                                Table, TableStyle, HRFlowable, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ACCENT = colors.HexColor("#b25600")
INK    = colors.HexColor("#1a1a1a")
MUTED  = colors.HexColor("#6b6b6b")
CODE_BG= colors.HexColor("#f4f4f2")
CODE_BD= colors.HexColor("#d8d6d2")
BOXBG  = colors.HexColor("#fbf1e8")   # warm tint for diagram nodes
BOXBD  = colors.HexColor("#e3b489")
ARROW  = colors.HexColor("#b25600")

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (scripts/..)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_root, "USER-GUIDE.pdf")

doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.9*inch, rightMargin=0.9*inch,
                        topMargin=0.85*inch, bottomMargin=0.75*inch,
                        title="Research-Vault User Guide", author="Chris Gilly")
W = doc.width
ss = getSampleStyleSheet()
title = ParagraphStyle("T", parent=ss["Title"], textColor=ACCENT, fontSize=22, leading=26, spaceAfter=2)
sub   = ParagraphStyle("S", parent=ss["Normal"], textColor=MUTED, fontSize=11, spaceAfter=12)
h2    = ParagraphStyle("H2", parent=ss["Heading2"], textColor=ACCENT, fontSize=13.5, leading=16, spaceBefore=15, spaceAfter=5)
body  = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10.3, leading=14.6, textColor=INK, spaceAfter=7)
note  = ParagraphStyle("N", parent=body, textColor=MUTED, fontSize=9.2, leading=12.4)
codest= ParagraphStyle("C", parent=ss["Code"], fontName="Courier", fontSize=8.2, leading=10.6, textColor=INK)
cap   = ParagraphStyle("cap", parent=note, alignment=1, spaceBefore=2, spaceAfter=10)

S=[]
def H(t): S.append(Paragraph(t, h2))
def P(t): S.append(Paragraph(t, body))
def CAP(t): S.append(Paragraph(t, cap))
def gap(h=6): S.append(Spacer(1,h))

def codebox(text, bg=CODE_BG, bd=CODE_BD):
    pre = Preformatted(text, codest)
    t = Table([[pre]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("BOX",(0,0),(-1,-1),0.6,bd),
        ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return t

def _multiline(d, cx, cy, label, fs, color):
    lines = label.split("\n"); lh = fs+2
    top = cy + (len(lines)-1)*lh/2.0 - fs/2.0 + 1
    for j,ln in enumerate(lines):
        d.add(String(cx, top - j*lh, ln, textAnchor="middle", fontSize=fs, fillColor=color, fontName="Helvetica"))

def flow_h(items, h=42, fs=8.6, gap_w=20):
    n=len(items); bw=(W-gap_w*(n-1))/n; d=Drawing(W,h); cy=h/2.0; x=0.0
    for i,lab in enumerate(items):
        d.add(Rect(x,0,bw,h,rx=6,ry=6,fillColor=BOXBG,strokeColor=BOXBD,strokeWidth=0.9))
        _multiline(d,x+bw/2.0,cy,lab,fs,INK)
        if i<n-1:
            x0=x+bw; x1=x+bw+gap_w
            d.add(Line(x0+2,cy,x1-3,cy,strokeColor=ARROW,strokeWidth=1.2))
            d.add(Polygon([x1-3,cy,x1-8,cy+3.4,x1-8,cy-3.4],fillColor=ARROW,strokeColor=ARROW))
        x+=bw+gap_w
    d.hAlign="CENTER"; return d

def flow_v(items, bh=32, fs=8.8, gap_h=16):
    n=len(items); h=n*bh+(n-1)*gap_h; d=Drawing(W,h); bw=W*0.66; x=(W-bw)/2.0; y=h-bh
    for i,lab in enumerate(items):
        d.add(Rect(x,y,bw,bh,rx=6,ry=6,fillColor=BOXBG,strokeColor=BOXBD,strokeWidth=0.9))
        _multiline(d,W/2.0,y+bh/2.0,lab,fs,INK)
        if i<n-1:
            d.add(Line(W/2.0,y,W/2.0,y-gap_h+3,strokeColor=ARROW,strokeWidth=1.2))
            d.add(Polygon([W/2.0,y-gap_h+3,W/2.0-3.4,y-gap_h+8,W/2.0+3.4,y-gap_h+8],fillColor=ARROW,strokeColor=ARROW))
        y-=bh+gap_h
    d.hAlign="CENTER"; return d

# ---------- Header ----------
S.append(Paragraph("The Research-Vault User Guide", title))
S.append(Paragraph("What it does, the mental model behind it, and how to use it day to day", sub))
S.append(HRFlowable(width="100%", thickness=1, color=CODE_BD, spaceAfter=10))

# ---------- What it is ----------
H("What it is, in one picture")
P("In essence, the vault is a filing cabinet that Claude knows how to read. It is an ordinary folder of plain-text markdown files &mdash; one file per project &mdash; and nothing in it is locked inside an application or a database. You can open it in any editor, search it with <font face='Courier'>grep</font>, version it with <font face='Courier'>git</font>, and read it in ten years. What the plugin adds is a shared set of conventions: where a task belongs, how a deadline is written, which file a new proposal goes in. Claude learns those conventions once, then keeps the files honest for you.")
P("That division is the whole idea. The files are yours; the plugin is the layer of habits on top of them.")
S.append(flow_h(["You", "Claude Code\n+ vault skills", "The vault\none .md per project"], h=46))
CAP("You drive through slash commands or plain language; Claude reads and writes the files. Obsidian, the HTML dashboard, and the email / calendar / chat connectors are optional surfaces onto the same files.")
P("Three parts are worth keeping separate in your mind. The <b>vault</b> is your data &mdash; the markdown files. The <b>plugin</b> is the convention layer &mdash; the commands and skills that encode how the vault is meant to be used. Everything else is optional surface area that reads the same files. Note that none of the optional pieces are required; the vault works fully offline with nothing more than Claude Code and a text editor.")

# ---------- Task syntax ----------
H("How a task is written")
P("A task is a GitHub-style checkbox line. On its own that is enough &mdash; <font face='Courier'>- [ ] call the program officer</font> is a perfectly good task. When you want a task to carry a deadline, a priority, or a person, you append small typed fields. In your files and on GitHub these are emoji (calendar, hourglass, check, up- and down-triangle); this PDF names them in words, because PDF fonts do not include emoji glyphs. The exact symbols are in the online USER-GUIDE.")
S.append(codebox(
"- [ ] **Send the revised draft to Sam**  [high]  [due 2026-07-10]  #sam-rivera\n"
"        high priority -----^      due date ----^     person ----^\n\n"
"# when finished:\n"
"- [x] **Send the revised draft to Sam**  [completed 2026-07-11]"))
rows = [["Field", "What it means", "Emoji in the file"],
        ["Due date", "when it is due", "calendar  +  YYYY-MM-DD"],
        ["Scheduled", "when to start", "hourglass  +  YYYY-MM-DD"],
        ["Completed", "on a done task", "check  +  YYYY-MM-DD"],
        ["Priority", "high or low", "up-triangle / down-triangle"],
        ["Person", "a collaborator", "#firstname-lastname"]]
tc = ParagraphStyle("tc", parent=body, fontSize=9.2, leading=12, spaceAfter=0)
mc = ParagraphStyle("mc", parent=codest, fontSize=8.4, leading=11)
data=[[Paragraph("<b>"+c+"</b>", tc) for c in rows[0]]]
for r in rows[1:]:
    data.append([Paragraph(r[0], tc), Paragraph(r[1], tc), Paragraph(html.escape(r[2]), mc)])
t = Table(data, colWidths=[1.2*inch, 2.2*inch, W-3.4*inch])
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),ACCENT),("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#faf9f7")]),
    ("LINEBELOW",(0,0),(-1,-1),0.4,CODE_BD),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
S.append(t); gap(4)
P("People are written as short handles rather than full names. The handle is a stable key; who it points to lives in your roster, so the same <font face='Courier'>#sam-rivera</font> means the same person across every file. It is straightforward to skip the fields entirely and still keep a working list; they earn their place only when structure is useful.")

# ---------- Everyday loop ----------
H("The everyday loop")
P("Most days, working the vault is a small loop: you capture things as they arrive, you do the work, you let Claude reconcile what changed back into the files, and you glance at the state when you need the big picture. Each step has a command, yet you rarely have to think in commands &mdash; plain language reaches the same skills.")
S.append(flow_h(["Capture", "Do the work", "Reconcile\n\"update the vault\"", "Review\n/status · /dashboard"], h=46))
CAP("The loop repeats daily; /journal logs the day alongside the reconcile step.")
P("<b>Capturing</b> is built around a ten-second rule: a thought should reach the right file before it evaporates. You give Claude one line, and it drops the task into the most likely project file, falling back to <font face='Courier'>inbox.md</font> when the home is ambiguous.")
S.append(codebox(
"You:    /capture email the program officer about the no-cost extension [high]\n\n"
"Claude: Added to grants-admin.md (Active):\n"
"        - [ ] **Email the program officer about the no-cost extension** [high]"))
P("<b>Reconciling</b> is the phrase <i>update the vault</i> &mdash; a small ritual with a specific meaning. It is not a single append, but a request to reconcile every project file the recent conversation touched: Claude advances or closes the tasks you actually moved, captures new ones, records decisions, and appends a short entry to today's daily note. In other words, it makes the files agree with what just happened. The deeper form, <font face='Courier'>/update --comprehensive</font>, also scans your connected email, calendar, chat, and trackers for commitments you never wrote down, and is honest about any source that is not connected.")

# ---------- Reviewing ----------
H("Seeing where things stand")
P("Two views answer the question. <font face='Courier'>/status</font> groups your proposals and projects into six buckets that march from idea to outcome:")
S.append(flow_h(["Untouched","Idea\nScoped","Drafting","Submitted","Awarded","Complete"], h=40, fs=7.8, gap_w=12))
CAP("Buckets come from the Status: line at the top of each project file; /status prints every bucket, even the empty ones.")
P("A file without a <font face='Courier'>**Status:**</font> line will not classify, so adding that one line is all it takes to bring a project into the view. The other view, <font face='Courier'>/dashboard</font>, regenerates <font face='Courier'>dashboard.html</font> &mdash; a self-contained browser page with filters for overdue, this-week, high-priority, and by-project. The dashboard is deliberately <b>read-only</b>: it is a window onto the files, not an editor of them, so a stray click cannot corrupt your notes. It needs Python 3; everything else here does not.")

# ---------- Memory ----------
H("The two-tier memory")
P("A vault is only useful if Claude understands your shorthand. When you write &ldquo;ask Sam about the PSR for Apollo,&rdquo; the words mean nothing without context. The memory supplies it, split into two tiers for the same reason a computer has both RAM and a disk &mdash; a small fast layer for what you touch constantly, and a large slow layer for everything else.")
S.append(flow_v([
    "Shorthand to decode\n(\"ask Sam about the PSR for Apollo\")",
    "Hot cache  -  vault CLAUDE.md\n(~30 people, active projects, daily terms)",
    "Deep storage  -  memory/\n(full glossary, a file per person & project)",
    "Not found?  Ask you once, then remember it"], bh=30, fs=8.4))
CAP("A hit at any level resolves the lookup; misses fall through to the next, and a final miss teaches the system.")
P("Over time the cheap, frequent things drift up into the hot cache and the stale things drift down, which keeps the fast layer both small and relevant. The payoff is that a handle like <font face='Courier'>#sam-rivera</font> or a codename like &ldquo;Apollo&rdquo; resolves the same way everywhere, and you can write in your own compressed language without losing the meaning.")

# ---------- Projects & proposals ----------
H("How projects and proposals are organized")
P("Every project is one markdown file, and <font face='Courier'>projects.md</font> is the manifest that lists them. A new line of work becomes its own file when it has its own deliverables and its own people; until then it can live as a task inside an existing file. Proposals get a little extra structure, because a grant has a lifecycle worth tracking: funding calls you are watching live in <font face='Courier'>proposal-solicitations.md</font> (grouped by the same six buckets), and science directions without a home call live in <font face='Courier'>proposal-ideas.md</font> until one is promoted into a real project. That is the machinery behind <font face='Courier'>/status</font>.")

# ---------- Without extras ----------
H("Working without the extras")
P("It is worth saying plainly what you can skip. The vault is fully functional with only Claude Code and a text editor. Obsidian is optional &mdash; it makes <font face='Courier'>dashboard.md</font> a live board and renders the metadata as real task fields. Python is optional and only powers <font face='Courier'>/dashboard</font>. The MCP connectors are optional and only feed <font face='Courier'>/update --comprehensive</font>. When something is missing, the affected command says so and the rest keeps working.")

# ---------- Appendix A ----------
H("Appendix A &mdash; command reference")
cmds = [["/start","Create the vault and interview you on first run; later, verify files and open today's note. Safe to re-run."],
        ["/capture <text>","Drop a one-line task into the most likely file (or inbox.md)."],
        ["/update","\"Update the vault\": reconcile every file the conversation touched; log the day."],
        ["/update --comprehensive","The above plus a scan of email, calendar, chat, and trackers."],
        ["/status","The six-bucket proposal / project status report."],
        ["/journal \"<text>\"","Append to today's daily note."],
        ["/triage","Walk inbox.md and route each loose item."],
        ["/dashboard","Regenerate the read-only dashboard.html (needs Python 3)."]]
cc = ParagraphStyle("cc", parent=codest, fontSize=8.3, leading=11)
data=[[Paragraph("<b>Command</b>",tc),Paragraph("<b>What it does</b>",tc)]]
for r in cmds: data.append([Paragraph(html.escape(r[0]),cc), Paragraph(r[1],tc)])
t=Table(data,colWidths=[1.85*inch,W-1.85*inch])
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),ACCENT),("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#faf9f7")]),
    ("LINEBELOW",(0,0),(-1,-1),0.4,CODE_BD),("VALIGN",(0,0),(-1,-1),"TOP"),
    ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
S.append(t); gap(2)
P("You rarely need the commands by name &mdash; plain language (&ldquo;what's open?&rdquo;, &ldquo;I finished the figure&rdquo;, &ldquo;add a task to the grant&rdquo;) reaches the same skills.")

# ---------- Appendix B ----------
H("Appendix B &mdash; vault layout")
S.append(codebox(
"<vault>/\n"
"  CLAUDE.md            hot-cache memory (your people/projects/prefs) + plugin pointer\n"
"  projects.md          the project manifest\n"
"  inbox.md             capture catch-all\n"
"  dashboard.md         Obsidian Tasks queries (live in-app board)\n"
"  dashboard.html       optional browser board, via /dashboard\n"
"  proposal-solicitations.md   funding calls you track (read by /status)\n"
"  proposal-ideas.md           idea-first proposal capture\n"
"  <project>.md         one file per project\n"
"  daily_notes/         one note per day, YYYY-MM-DD.md\n"
"  memory/              glossary.md, people/<handle>.md, projects/<name>.md, context/"))
S.append(Paragraph("The plugin is the convention layer, versioned on GitHub; your vault is your own data folder, which you back up separately. The literal task-metadata emoji and a fuller worked example are in the online USER-GUIDE.md.", note))

def footer(c,d):
    c.saveState(); c.setFont("Helvetica",8); c.setFillColor(MUTED)
    c.drawString(0.9*inch,0.5*inch,"research-vault user guide")
    c.drawRightString(letter[0]-0.9*inch,0.5*inch,"Page %d"%d.page); c.restoreState()

doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("WROTE", out)
