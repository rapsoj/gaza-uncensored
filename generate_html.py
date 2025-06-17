import os
import re
from datetime import datetime

video_dir = "videos"
date_dir = "dates"
caption_dir = "video_captions"

def numeric_key(filename):
    match = re.match(r"(\d+)", filename)
    return int(match.group(1)) if match else float('inf')

def parse_date(date_str):
    # Example: "Monday, June 16th, 2025"
    try:
        # Remove ordinal suffixes: "16th" → "16"
        date_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        return datetime.strptime(date_clean, "%A, %B %d, %Y")
    except Exception:
        return datetime.min  # fallback for bad/missing dates

video_entries = []
for video in os.listdir(video_dir):
    if not video.endswith(".mp4"):
        continue

    base_name = os.path.splitext(video)[0]

    # Date
    date_path = os.path.join(date_dir, base_name + ".txt")
    try:
        with open(date_path, "r") as df:
            full_date = df.read().strip()
            parsed_date = parse_date(full_date)
    except FileNotFoundError:
        full_date = "Unknown date"
        parsed_date = datetime.min

    # Caption
    caption_path = os.path.join(caption_dir, base_name + ".txt")
    try:
        with open(caption_path, "r") as cf:
            caption = cf.read().strip().replace('\n', ' ')
    except FileNotFoundError:
        caption = ""

    video_entries.append({
        "src": f"{video_dir}/{video}",
        "date": full_date,
        "parsed_date": parsed_date,
        "caption": caption
    })

# 🔁 Sort by parsed_date (most recent first)
video_entries.sort(key=lambda x: x["parsed_date"], reverse=True)

# 🔄 Create JS objects
video_objects = [
    f'{{ src: "{v["src"]}", date: "{v["date"]}", caption: `{v["caption"]}` }}'
    for v in video_entries
]

html_template = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Uncensored Gaza</title>
  <style>
    body {{
      background: #000;
      margin: 0;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      align-items: center;
      height: 100vh;
      color: white;
      font-family: Arial, sans-serif;
    }}
    .date-display {{
      font-size: 1.2rem;
      margin: 20px 0 10px;
      color: #ccc;
    }}
    video {{
      height: 70vh;
      width: auto;
      background: black;
      object-fit: contain;
      display: block;
    }}
    .caption-display {{
      font-size: 1rem;
      margin-top: 10px;
      margin-bottom: 10px;
      max-width: 90%;
      text-align: center;
      color: #aaa;
    }}
    .intro-message {{
      font-size: 1.5rem;
      margin-top: 30px;
      margin-bottom: 10px;
      color: red;
      text-align: center;
    }}
    .controls {{
      margin-top: 10px;
      display: flex;
      align-items: center;
      gap: 20px;
    }}
    button {{
      font-size: 1.5rem;
      padding: 10px 20px;
      cursor: pointer;
      background: #222;
      color: white;
      border: none;
      border-radius: 5px;
      user-select: none;
    }}
    button:hover {{
      background: #555;
    }}
  </style>
</head>
<body>
  <div class="intro-message">It still happens, even if you look away.</div>
  <div class="date-display" id="dateDisplay"></div>
  <video id="player" controls autoplay muted></video>
  <div class="caption-display" id="captionDisplay"></div>
  <div class="controls">
    <button id="prevBtn" aria-label="Previous video">⬅️ Previous</button>
    <button id="nextBtn" aria-label="Next video">Next ➡️</button>
  </div>

  <script>
    const videos = [
      {video_list_js}
    ];

    let current = 0;
    const player = document.getElementById('player');
    const dateDisplay = document.getElementById('dateDisplay');
    const captionDisplay = document.getElementById('captionDisplay');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    function loadVideo(index) {{
      if (index >= 0 && index < videos.length) {{
        current = index;
        player.src = videos[current].src;
        dateDisplay.textContent = videos[current].date;
        captionDisplay.textContent = videos[current].caption;
        player.play();
      }}
    }}

    loadVideo(current);

    player.addEventListener('ended', () => {{
      if (current < videos.length - 1) {{
        loadVideo(current + 1);
      }}
    }});

    prevBtn.addEventListener('click', () => {{
      if (current > 0) {{
        loadVideo(current - 1);
      }}
    }});

    nextBtn.addEventListener('click', () => {{
      if (current < videos.length - 1) {{
        loadVideo(current + 1);
      }}
    }});
  </script>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_template)

print("✅ HTML updated!")
