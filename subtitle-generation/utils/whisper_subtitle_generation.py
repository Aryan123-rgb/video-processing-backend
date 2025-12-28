import whisper 
from datetime import timedelta

def format_timestamp(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((seconds - total_seconds) * 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def generate_subtitle(video_path: str):
    model = whisper.load_model("small")
    result = model.transcribe(
        video_path,
        language="en",
        fp16=False
    )
    subs = []
    for segment in result['segments']:
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        subs.append(f"{segment['id'] + 1}\n")
        subs.append(f"{start} --> {end}\n")
        subtitle = str(segment['text']).lstrip()
        subs.append(f"{subtitle}\n\n")
        
    subtitle = "".join(subs)
    return subtitle 
    