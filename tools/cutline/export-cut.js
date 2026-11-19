// Approved Cutline timeline -> one tight cut file for the shorts pipeline (Step 5 of docs/editing-workflow.md).
// Reads the project from the running Cutline server, takes the bottom video track in timeline order and cuts the
// source ranges out of the original media (frame-accurate re-encode), so the house-style build/render stays ours.
//   node tools/cutline/export-cut.js <projectId> <out.mp4>      (writes <out>.ranges.json next to it)
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const [id, out] = process.argv.slice(2);
if (!id || !out) { console.error("usage: node export-cut.js <projectId> <out.mp4>"); process.exit(1); }
const PORT = process.env.CUTLINE_PORT || 4100;
const DATA = path.resolve(__dirname, "../../output/cutline/data");

(async () => {
  const res = await fetch(`http://127.0.0.1:${PORT}/api/projects/${id}`);
  if (!res.ok) throw new Error(`Cutline: ${res.status} ${await res.text()}`);
  const body = await res.json();
  const p = body.project || body;
  const assets = Object.fromEntries(p.assets.map((a) => [a.id, a]));
  const video = p.tracks.filter((t) => t.kind === "video" && !t.hidden);
  if (!video.length) throw new Error("no visible video track");
  const clips = video[0].clips.filter((c) => c.type === "video").sort((a, b) => a.start - b.start);
  if (!clips.length) throw new Error("bottom video track is empty");

  // shortcut: speed changes, extra tracks and overlays are not carried over (listed below), upgrade if reviews use them.
  const ignored = [];
  for (const t of p.tracks.filter((t) => t !== video[0])) for (const c of t.clips) ignored.push(`${t.name}: ${c.type} ${c.id} at ${c.start}s`);
  const ranges = clips.map((c) => {
    if (c.speed && c.speed !== 1) throw new Error(`${c.id} has speed ${c.speed}; set it back to 1 or handle it by hand`);
    const a = assets[c.assetId];
    return { clip: c.id, src: path.join(DATA, a.src), start: c.sourceStart, end: c.sourceStart + c.duration, muted: c.muted };
  });

  const args = [], parts = [];
  ranges.forEach((r, i) => {
    args.push("-ss", r.start.toFixed(3), "-t", (r.end - r.start).toFixed(3), "-i", r.src);
    parts.push(`[${i}:v:0]setpts=PTS-STARTPTS[v${i}];[${i}:a:0]asetpts=PTS-STARTPTS${r.muted ? ",volume=0" : ""}[a${i}]`);
  });
  const cat = ranges.map((_, i) => `[v${i}][a${i}]`).join("") + `concat=n=${ranges.length}:v=1:a=1[v][a]`;
  execFileSync("ffmpeg", ["-v", "error", "-y", ...args, "-filter_complex", parts.join(";") + ";" + cat,
    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "256k", out], { stdio: "inherit" });
  fs.writeFileSync(out.replace(/\.mp4$/, "") + ".ranges.json", JSON.stringify({ project: id, ranges, ignored }, null, 1));
  const total = ranges.reduce((s, r) => s + r.end - r.start, 0);
  console.log(`${out}: ${ranges.length} ranges, ${total.toFixed(2)} s`);
  if (ignored.length) console.log(`NOT carried over (redo in the build step):\n  ${ignored.join("\n  ")}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
