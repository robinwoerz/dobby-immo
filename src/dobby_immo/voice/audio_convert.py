"""Convert Telegram voice blobs (OGG Opus) for APIs that expect WAV."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


class AudioConversionError(RuntimeError):
    """Raised when ffmpeg cannot decode or encode the input audio."""


async def ogg_opus_to_wav(ogg_bytes: bytes) -> bytes:
    """Decode OGG/Opus from stdin and emit mono 16 kHz PCM WAV on stdout.

    Requires ``ffmpeg`` on PATH.

    Args:
        ogg_bytes: Raw OGG Opus file contents (e.g. Telegram voice).

    Returns:
        WAV file bytes.

    Raises:
        AudioConversionError: If ffmpeg is missing or exits non-zero.
    """
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        "pipe:0",
        "-f",
        "wav",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        "pipe:1",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=ogg_bytes)
    if proc.returncode != 0:
        err = stderr.decode(errors="replace").strip() or "ffmpeg failed"
        logger.warning("ffmpeg voice conversion failed: %s", err)
        raise AudioConversionError(err)
    return stdout
