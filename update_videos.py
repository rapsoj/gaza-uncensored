from telethon.sync import TelegramClient
import os
from datetime import datetime

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

video_dir = 'videos'
text_dir = 'video_texts'
date_dir = 'dates'

# Ensure directories exist
os.makedirs(video_dir, exist_ok=True)
os.makedirs(text_dir, exist_ok=True)
os.makedirs(date_dir, exist_ok=True)

# Preload list of already downloaded video IDs
downloaded_ids = {
    f.split('.')[0] for f in os.listdir(video_dir) if f.endswith('.mp4')
}

# Helper to add ordinal suffix to the day
def format_ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Format date to "Monday, June 15th, 2025"
def format_date(dt):
    day_with_suffix = format_ordinal(dt.day)
    return dt.strftime(f"%A, %B {day_with_suffix}, %Y")

async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        print("Connected!")

        messages = await client.get_messages('me', limit=100)

        for msg in messages:
            if msg.video:
                msg_id_str = str(msg.id)
                if msg_id_str in downloaded_ids:
                    continue

                # Save video
                video_path = os.path.join(video_dir, f"{msg_id_str}.mp4")
                print(f"Downloading video {msg_id_str} → {video_path}")
                await msg.download_media(file=video_path)

                # Save associated text
                text_path = os.path.join(text_dir, f"{msg_id_str}.txt")
                caption = msg.text or ""
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(caption)

                # Save friendly formatted date
                date_path = os.path.join(date_dir, f"{msg_id_str}.txt")
                pretty_date = format_date(msg.date)
                with open(date_path, "w", encoding="utf-8") as f:
                    f.write(pretty_date)
        print("All videos up to date.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())