from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_path: str):
    segments, _ = model.transcribe(audio_path, beam_size=5)

    return " ".join(segment.text for segment in segments).strip()
