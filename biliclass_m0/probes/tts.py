import time
import wave

from ..paths import output_root


def run() -> dict:
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = speaker.GetVoices()
        available = []
        audio = []
        selected = {}
        for index in range(voices.Count):
            token = voices.Item(index)
            locales = token.GetAttribute("Language").split(";")
            language_ids = [int(value, 16) & 0x3FF for value in locales if value]
            language = "en" if 9 in language_ids else "vi" if 42 in language_ids else "other"
            available.append({"id": token.Id, "name": token.GetDescription(), "language": language})
            if language in ("en", "vi") and language not in selected:
                selected[language] = token
        for language, token in selected.items():
            path = output_root() / f"voice-{language}.wav"
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            started = time.perf_counter()
            try:
                stream.Open(str(path), 3, False)
                speaker.Voice = token
                speaker.AudioOutputStream = stream
                speaker.Speak(
                    "Please explain your answer to the class."
                    if language == "en"
                    else "Các em hãy giải thích câu trả lời của mình."
                )
            finally:
                stream.Close()
            with wave.open(str(path), "rb") as wav:
                frames, rate = wav.getnframes(), wav.getframerate()
            if frames <= 0:
                raise RuntimeError("TTS tạo tệp âm thanh rỗng")
            audio.append(
                {
                    "language": language,
                    "voice": token.GetDescription(),
                    "path": str(path),
                    "synthesis_ms": round((time.perf_counter() - started) * 1000, 1),
                    "duration_s": round(frames / rate, 2),
                    "bytes": path.stat().st_size,
                }
            )
        return {
            "status": "passed" if "en" in selected else "needs_setup",
            "voices": available,
            "audio": audio,
            "vi_available": "vi" in selected,
            "notes": [
                "Đã tạo WAV bằng SAPI local; không phát loa trong probe.",
                "SAPI voice inventory không đại diện tất cả giọng WinRT/Narrator.",
                "Thiếu giọng VI: vẫn dùng VI Rescue dạng chữ, không giả giọng đã có.",
            ],
        }
    finally:
        pythoncom.CoUninitialize()
