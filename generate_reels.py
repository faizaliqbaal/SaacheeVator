#!/usr/bin/env python3
"""
AI Instagram Reels Generator for Men's Mental Health & Motivation
Automates:
- Scripting & Hook selection
- Natural neural TTS Voiceover (Edge TTS / ElevenLabs)
- Ken Burns Cinematic Video Animation from 9:16 vertical portraits
- Aesthetic Glassmorphism Hook Banner & Dynamic Subtitle burn-in
- Instagram Captions, Hashtags, and Metadata export
"""

import os
import sys
import json
import asyncio
import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import mutagen.mp3
import imageio_ffmpeg
import edge_tts

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Default font paths (Ubuntu / Debian)
DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
if not os.path.exists(DEFAULT_FONT_PATH):
    DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

REELS_DATABASE = [
    {
        "id": "reel_01_silent_battles",
        "theme": "Men's Mental Health & Inner Strength",
        "image": "persona_empathy.jpg",
        "hook": "TO THE MAN FIGHTING IN SILENCE",
        "script": "I know you are carrying a lot right now. You show up for everyone else, you handle your business, and you rarely complain. But taking a breath is not quitting. You are stronger than your heaviest days, and you are doing better than you think. Keep going.",
        "diffusion_prompt": "Vertical 9:16 photorealistic cinematic video of the 22yo modern Indian woman in warm cozy lounge, speaking earnestly directly to camera. Natural organic hand gestures with open palms emphasizing her points, gentle head nods and tilts, empathetic micro-expressions, subtle shoulder breathing, photorealistic human physics, 4k 60fps.",
        "caption": """Most men fight their heaviest wars without telling a single soul. 👑

You don't have to carry the whole world on your shoulders every single day. Taking a moment to breathe and reset isn't quitting—it's preparing for the next victory.

Drop a 🖤 if you needed this reminder today.
Save this for when you need a reset.

#mensmentalhealth #unspokenbattles #innerstrength #silentbattles #mindsetshift #selfimprovement #stoicism #brotherhood #resilience""",
        "voice": "en-IN-NeerjaExpressiveNeural",
        "rate": "+0%",
        "pitch": "-2Hz"
    },
    {
        "id": "reel_02_discipline_standard",
        "theme": "Morning Discipline & Tough Love",
        "image": "persona_fitness.jpg",
        "hook": "MOTIVATION FADES. STANDARDS DON'T.",
        "script": "Stop waiting until you feel like it. The version of you that reaches your goals does not negotiate with the alarm clock or his excuses. Discipline is the ultimate form of self-respect. Get up, lock in, and handle your work today.",
        "diffusion_prompt": "Vertical 9:16 cinematic video of the 22yo modern Indian woman in chic gym activewear at sunrise, speaking with confident focused intensity. Natural assertive hand gestures, firm confident nods, subtle head movement, determined warm smile, photorealistic fluid human motion, 4k.",
        "caption": """You don't need another motivational quote. You need a higher standard. 🔥

The man who shows up even when he doesn't feel like it will always beat the man who only works when inspired. 

Share this with a brother who needs to lock in.
Double tap if you're executing today.

#disciplineovermotivation #mensmindset #workoutmotivation #hardworkpaysoff #focusmode #grindset #fitnessmindset #brotherhood""",
        "voice": "en-IN-NeerjaExpressiveNeural",
        "rate": "+4%",
        "pitch": "+0Hz"
    },
    {
        "id": "reel_03_self_worth",
        "theme": "Boundaries & Personal Value",
        "image": "persona_lifestyle.jpg",
        "hook": "BUILD IN SILENCE. LET RESULTS SPEAK.",
        "script": "You do not need to beg for respect or chase validation. Build your skills, protect your peace, and honor your own boundaries. When you become a man who respects himself, the right people and opportunities follow naturally.",
        "diffusion_prompt": "Vertical 9:16 cinematic lifestyle video of the 22yo modern Indian woman in luxury cafe setting, speaking calmly about standards. Natural conversational hand gestures, glancing thoughtfully, smiling warmly, relaxed elegant posture, fluid organic motion, 4k.",
        "caption": """A high-value life isn't built on loud words—it's built on quiet execution. 📈

Stop trying to convince people of your worth. Build your foundation, stack your small wins, and let your results do all the talking.

Save this as your daily standard.

#highvalueman #boundaries #selfworth #innerpeace #stoicmindset #mensgrowth #discipline #leadership #quietconfidence""",
        "voice": "en-IN-NeerjaExpressiveNeural",
        "rate": "+0%",
        "pitch": "-2Hz"
    }
]


def create_hook_overlay(hook_text: str, handle: str, output_path: Path, width=1080, height=1920):
    """Creates a sleek, modern glassmorphic top hook banner and account watermark."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font_hook = ImageFont.truetype(DEFAULT_FONT_PATH, 42)
        font_handle = ImageFont.truetype(DEFAULT_FONT_PATH, 28)
        font_badge = ImageFont.truetype(DEFAULT_FONT_PATH, 22)
    except Exception:
        font_hook = ImageFont.load_default()
        font_handle = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # Draw Category Badge (Top pill)
    badge_text = "DAILY REMINDER"
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    badge_x = (width - bw) // 2
    badge_y = 190

    # Badge background
    draw.rounded_rectangle(
        [badge_x - 18, badge_y - 8, badge_x + bw + 18, badge_y + bh + 8],
        radius=14,
        fill=(220, 160, 40, 220)  # Warm Gold Accent
    )
    draw.text((badge_x, badge_y), badge_text, font=font_badge, fill=(20, 20, 20, 255))

    # Draw Main Hook Banner Card
    hook_lines = []
    words = hook_text.split()
    current_line = []
    for w in words:
        current_line.append(w)
        line_str = " ".join(current_line)
        bbox = draw.textbbox((0, 0), line_str, font=font_hook)
        if (bbox[2] - bbox[0]) > 860:
            current_line.pop()
            hook_lines.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        hook_lines.append(" ".join(current_line))

    line_height = 54
    total_hook_h = len(hook_lines) * line_height
    box_w = 940
    box_h = total_hook_h + 50
    box_x = (width - box_w) // 2
    box_y = badge_y + bh + 24

    # Dark translucent card with subtle glowing border
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=24,
        fill=(15, 18, 24, 210),
        outline=(255, 255, 255, 90),
        width=2
    )

    # Render Hook Text centered
    for i, line in enumerate(hook_lines):
        bbox_l = draw.textbbox((0, 0), line, font=font_hook)
        lw = bbox_l[2] - bbox_l[0]
        lx = (width - lw) // 2
        ly = box_y + 24 + i * line_height
        # Soft shadow
        draw.text((lx + 2, ly + 2), line, font=font_hook, fill=(0, 0, 0, 220))
        draw.text((lx, ly), line, font=font_hook, fill=(255, 255, 255, 255))

    # Watermark / Handle at the bottom center
    if handle:
        handle_text = handle if handle.startswith("@") else f"@{handle}"
        bbox_h = draw.textbbox((0, 0), handle_text, font=font_handle)
        hw = bbox_h[2] - bbox_h[0]
        hx = (width - hw) // 2
        hy = height - 160
        # Pill behind handle
        draw.rounded_rectangle(
            [hx - 16, hy - 6, hx + hw + 16, hy + 36],
            radius=16,
            fill=(0, 0, 0, 140)
        )
        draw.text((hx, hy), handle_text, font=font_handle, fill=(240, 240, 240, 220))

    img.save(output_path, "PNG")


async def generate_voiceover(text: str, voice: str, rate: str, pitch: str, audio_path: Path, sub_path: Path):
    """Generates natural neural TTS and synced subtitle file."""
    comm = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    sub_maker = edge_tts.SubMaker()
    
    with open(audio_path, "wb") as f_audio:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f_audio.write(chunk["data"])
            else:
                sub_maker.feed(chunk)
                
    # Write SRT subtitles
    srt_content = sub_maker.get_srt()
    with open(sub_path, "w", encoding="utf-8") as f_sub:
        f_sub.write(srt_content)


def render_reel(
    image_path: Path,
    audio_path: Path,
    sub_path: Path,
    overlay_path: Path,
    output_mp4: Path,
    duration: float
):
    """Renders 1080x1920 9:16 vertical reel using FFmpeg with Ken Burns effect and burned-in subtitles."""
    total_frames = int(duration * 30) + 10
    
    # Use relative path so libass/ffmpeg opens it without path escaping quirks
    sub_rel = os.path.relpath(sub_path, start=os.getcwd()).replace("\\", "/")
    sub_filter = (
        f"subtitles={sub_rel}:force_style="
        "'FontName=Liberation Sans,FontSize=24,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=2,Alignment=2,MarginV=300'"
    )

    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0007,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1080x1920:fps=30[bg];"
        f"[bg][1:v]overlay=0:0[with_hook];"
        f"[with_hook]{sub_filter}[finalv]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(overlay_path),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[finalv]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{duration + 0.5:.2f}",
        str(output_mp4)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed with code {res.returncode}:\n{res.stderr}")


def render_talking_avatar(
    image_path: Path,
    audio_path: Path,
    sub_path: Path,
    overlay_path: Path,
    output_mp4: Path
):
    """Generates a natural speaking avatar video using SadTalker on local GPU, then burns hook and subtitles."""
    sadtalker_dir = BASE_DIR / "SadTalker"
    checkpoints_dir = sadtalker_dir / "checkpoints"
    temp_result_dir = OUTPUT_DIR / "talking_temp"
    temp_result_dir.mkdir(parents=True, exist_ok=True)
    
    python_bin = BASE_DIR / "sadtalker_env" / "bin" / "python"
    env = os.environ.copy()
    env["PATH"] = f"{BASE_DIR}/sadtalker_env/bin:{env.get('PATH', '')}"

    # Step A: Run SadTalker
    print("    → Animating facial speech and head motion on GPU (SadTalker)...")
    cmd_sadtalker = [
        str(python_bin), str(sadtalker_dir / "inference.py"),
        "--driven_audio", str(audio_path),
        "--source_image", str(image_path),
        "--result_dir", str(temp_result_dir),
        "--checkpoint_dir", str(checkpoints_dir),
        "--still",
        "--preprocess", "full",
        "--size", "512"
    ]
    res = subprocess.run(cmd_sadtalker, capture_output=True, text=True, env=env)
    if res.returncode != 0:
        raise RuntimeError(f"SadTalker failed:\n{res.stderr[-1000:]}")

    # Find the output video (SadTalker saves as [timestamp].mp4)
    mp4_files = sorted(temp_result_dir.glob("*.mp4"), key=os.path.getmtime, reverse=True)
    if not mp4_files:
        raise FileNotFoundError("SadTalker did not produce an MP4 file in result directory")
    raw_talking_mp4 = mp4_files[0]

    # Step B: Composite into 1080x1920 with hook overlay and subtitles
    print("    → Compositing 1080x1920 Reel with hook badge & dynamic subtitles...")
    sub_rel = os.path.relpath(sub_path, start=os.getcwd()).replace("\\", "/")
    sub_filter = (
        f"subtitles={sub_rel}:force_style="
        "'FontName=Liberation Sans,FontSize=24,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=2,Alignment=2,MarginV=300'"
    )
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        f"[bg][1:v]overlay=0:0[with_hook];"
        f"[with_hook]{sub_filter}[finalv]"
    )
    cmd_composite = [
        str(BASE_DIR / "sadtalker_env" / "bin" / "ffmpeg"), "-y",
        "-i", str(raw_talking_mp4),
        "-i", str(overlay_path),
        "-filter_complex", filter_complex,
        "-map", "[finalv]",
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(output_mp4)
    ]
    res_comp = subprocess.run(cmd_composite, capture_output=True, text=True, env=env)
    if res_comp.returncode != 0:
        raise RuntimeError(f"FFmpeg compositing failed:\n{res_comp.stderr}")


def render_diffusion_video(
    video_path: Path,
    audio_path: Path,
    sub_path: Path,
    overlay_path: Path,
    output_mp4: Path,
    duration: float
):
    """Composites a realistic diffusion video (from Kling, Runway, or Hailuo) with synchronized audio, hook card & subtitles."""
    sub_rel = os.path.relpath(sub_path, start=os.getcwd()).replace("\\", "/")
    sub_filter = (
        f"subtitles={sub_rel}:force_style="
        "'FontName=Liberation Sans,FontSize=24,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=2,Alignment=2,MarginV=300'"
    )
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        f"[bg][1:v]overlay=0:0[with_hook];"
        f"[with_hook]{sub_filter}[finalv]"
    )
    cmd = [
        str(BASE_DIR / "sadtalker_env" / "bin" / "ffmpeg"), "-y",
        "-stream_loop", "-1",
        "-i", str(video_path),
        "-i", str(overlay_path),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[finalv]",
        "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{duration + 0.3:.2f}",
        str(output_mp4)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg video compositing failed:\n{res.stderr}")


async def process_single_reel(reel_data: dict, handle: str = "@mindset.elevate", lip_sync: bool = False, input_video: str = None):
    reel_id = reel_data["id"]
    suffix = "_realistic" if input_video else ("_talking" if lip_sync else "")
    print(f"\n==========================================")
    print(f"▶ Processing Reel: {reel_id} ({reel_data['theme']})")
    print(f"==========================================")

    img_file = ASSETS_DIR / reel_data["image"]
    if not img_file.exists():
        raise FileNotFoundError(f"Image asset missing: {img_file}")

    audio_file = OUTPUT_DIR / f"{reel_id}_voice.mp3"
    sub_file = OUTPUT_DIR / f"{reel_id}_sub.srt"
    overlay_file = OUTPUT_DIR / f"{reel_id}_hook.png"
    output_mp4 = OUTPUT_DIR / f"{reel_id}{suffix}.mp4"
    meta_json = OUTPUT_DIR / f"{reel_id}{suffix}_meta.json"
    caption_txt = OUTPUT_DIR / f"{reel_id}{suffix}_caption.txt"

    # Step 1: Generate Voiceover & Subtitles
    print(f"[1/4] Generating expressive voiceover ({reel_data['voice']})...")
    await generate_voiceover(
        text=reel_data["script"],
        voice=reel_data["voice"],
        rate=reel_data.get("rate", "+0%"),
        pitch=reel_data.get("pitch", "+0Hz"),
        audio_path=audio_file,
        sub_path=sub_file
    )

    # Step 2: Calculate Duration
    audio_info = mutagen.mp3.MP3(str(audio_file))
    duration = audio_info.info.length
    print(f"[2/4] Voiceover completed. Duration: {duration:.2f}s")

    # Step 3: Create Hook Overlay Card
    print(f"[3/4] Generating glassmorphic hook overlay card...")
    create_hook_overlay(
        hook_text=reel_data["hook"],
        handle=handle,
        output_path=overlay_file
    )

    # Step 4: Render MP4 with FFmpeg
    if input_video:
        print(f"[4/4] Compositing photorealistic diffusion video ({input_video})...")
        render_diffusion_video(
            video_path=Path(input_video),
            audio_path=audio_file,
            sub_path=sub_file,
            overlay_path=overlay_file,
            output_mp4=output_mp4,
            duration=duration
        )
    elif lip_sync:
        print(f"[4/4] Rendering realistic GPU-accelerated talking face with SadTalker...")
        render_talking_avatar(
            image_path=img_file,
            audio_path=audio_file,
            sub_path=sub_file,
            overlay_path=overlay_file,
            output_mp4=output_mp4
        )
    else:
        print(f"[4/4] Rendering 1080x1920 Ken Burns video with burned-in subtitles...")
        render_reel(
            image_path=img_file,
            audio_path=audio_file,
            sub_path=sub_file,
            overlay_path=overlay_file,
            output_mp4=output_mp4,
            duration=duration
        )

    # Save Instagram Caption & Metadata
    with open(caption_txt, "w", encoding="utf-8") as f:
        f.write(reel_data["caption"])

    metadata = {
        "id": reel_id,
        "theme": reel_data["theme"],
        "video_file": str(output_mp4),
        "mode": "diffusion_video" if input_video else ("sadtalker_gpu" if lip_sync else "ken_burns"),
        "duration_seconds": round(duration, 2),
        "resolution": "1080x1920 (9:16)",
        "hook": reel_data["hook"],
        "voiceover_script": reel_data["script"],
        "diffusion_prompt": reel_data.get("diffusion_prompt", ""),
        "instagram_caption": reel_data["caption"],
        "suggested_audio": "Trending Piano / Lo-Fi ambient audio lowered to 15% volume"
    }
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✔ Successfully created: {output_mp4.name} ({output_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return metadata


def print_diffusion_prompts():
    print("\n" + "="*70)
    print("🎬 PHOTOREALISTIC DIFFUSION VIDEO PROMPT CHEAT-SHEET (KLING / RUNWAY / HAILUO)")
    print("="*70)
    print("\nHow to use:")
    print("1. Go to Kling AI (https://klingai.com) or Runway Gen-3 (https://app.runwayml.com)")
    print("2. Choose 'Image to Video' (Upload the corresponding reference image from assets/)")
    print("3. Paste the prompt below and generate a 5s-10s clip.")
    print("4. Download the video and run: python generate_reels.py --index X --input-video your_video.mp4\n")
    
    for i, reel in enumerate(REELS_DATABASE):
        print(f"\n--- [Reel {i}: {reel['theme']}] ---")
        print(f"📷 Base Image: assets/{reel['image']}")
        print(f"💡 On-Screen Hook: {reel['hook']}")
        print(f"✨ Diffusion Prompt:\n{reel['diffusion_prompt']}")
    print("\n" + "="*70 + "\n")


async def main():
    parser = argparse.ArgumentParser(description="AI Instagram Reels Batch Generator")
    parser.add_argument("--batch", action="store_true", help="Generate all predefined sample reels")
    parser.add_argument("--index", type=int, default=0, help="Generate a specific reel index (0, 1, or 2)")
    parser.add_argument("--handle", type=str, default="@mindset.elevate", help="Instagram handle watermark")
    parser.add_argument("--lip-sync", action="store_true", help="Enable GPU-accelerated talking lip-sync animation (SadTalker)")
    parser.add_argument("--input-video", type=str, default=None, help="Path to photorealistic diffusion video (Kling/Runway/Hailuo) to package")
    parser.add_argument("--prompts", action="store_true", help="Print tested prompt cheat-sheet for Kling AI & Runway Gen-3")
    args = parser.parse_args()

    if args.prompts:
        print_diffusion_prompts()
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.batch:
        results = []
        for reel in REELS_DATABASE:
            res = await process_single_reel(reel, handle=args.handle, lip_sync=args.lip_sync, input_video=args.input_video)
            results.append(res)
        print("\n🎉 ALL BATCH REELS GENERATED SUCCESSFULLY!")
    else:
        reel = REELS_DATABASE[args.index]
        await process_single_reel(reel, handle=args.handle, lip_sync=args.lip_sync, input_video=args.input_video)


if __name__ == "__main__":
    asyncio.run(main())
