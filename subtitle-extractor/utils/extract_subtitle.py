import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def extract_subtitle(video_id: str, video_path: str) -> str | None:
    logger.info(f"Starting subtitle extraction for {video_id}")

    try:
        # Step 1: Probe subtitle streams
        ffprobe_cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "s",
            "-show_entries", "stream=index:stream_tags=language:stream_disposition=default",
            "-of", "json",
            video_path
        ]

        result = subprocess.run(
            ffprobe_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        streams = json.loads(result.stdout).get("streams", [])

        # Step 2: Pick English subtitle
        subtitle_index = None

        for s in streams:
            lang = s.get("tags", {}).get("language", "").lower()
            default = s.get("disposition", {}).get("default", 0)
            if lang == "eng" and default == 1:
                subtitle_index = s["index"]
                break

        if subtitle_index is None:
            for s in streams:
                if s.get("tags", {}).get("language", "").lower() == "eng":
                    subtitle_index = s["index"]
                    break

        if subtitle_index is None:
            logger.warning(f"No English subtitles found for {video_id}")
            return None

        # Step 3: Extract subtitle to stdout
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-map", f"0:{subtitle_index}",
            "-c:s", "copy",
            "-f", "srt",
            "-"
        ]

        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        subtitle_text = result.stdout.strip()

        logger.info(f"Subtitle extracted successfully for {video_id}")
        return subtitle_text

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg/FFprobe failed: {e.stderr}")
        raise Exception(f"Video processing error: {e.stderr}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
