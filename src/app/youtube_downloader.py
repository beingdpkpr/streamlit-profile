import zipfile
from pathlib import Path

import yt_dlp


class YouTubeDownloader:
    def __init__(self, download_path="downloads"):
        """Initialize downloader with a download directory."""
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)
        BASE_DIR = Path(__file__).resolve().parent
        self.BUNDLED_FFMPEG = BASE_DIR / "ffmpeg" / "bin"
        self.BUNDLED_FFMPEG = f"C:\ffmpeg\bin"

    def download_video(self, _url, _quality="best", _progress=None, _status=None):
        def hook(d):
            percentage = d["downloaded_bytes"] / d["total_bytes"]
            if _progress:
                _progress.progress(percentage)
            if _status:
                file_name = d["filename"]
                file_name = (file_name[:30] + "…") if len(file_name) > 30 else file_name
                _status.info(f"{d['status']}: {file_name} - {percentage * 100:.0f}%")

        ydl_opts = {
            "format": (
                "bestvideo+bestaudio/best"
                if _quality == "best"
                else f"bestvideo[height<={_quality[:-1]}]+bestaudio/best"
            ),
            "outtmpl": str(self.download_path / "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "progress_hooks": [hook],
            "quiet": False,
            "noprogress": False,
            "cachedir": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(_url, download=True)
                filename = ydl.prepare_filename(info)
                return True, info["title"], filename
        except Exception as e:
            return False, str(e), None

    def download_audio(self, _url, _format="mp3", _progress=None, _status=None):
        """Download only audio from video."""

        def hook(d):
            percentage = d["downloaded_bytes"] / d["total_bytes"]
            if _progress:
                _progress.progress(percentage)
            if _status:
                file_name = d["filename"]
                file_name = (file_name[:30] + "…") if len(file_name) > 30 else file_name
                _status.info(f"{d['status']}: {file_name} - {percentage * 100:.0f}%")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(self.download_path / "%(title)s.%(ext)s"),
            "ffmpeg_location": self.BUNDLED_FFMPEG,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": _format,
                    "preferredquality": "192",
                }
            ],
            "progress_hooks": [hook],
        }
        try:
            # print(f"Downloading Audio: {self.download_path}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(_url, download=True)
                filename = str(self.download_path / f"{info['title']}.{_format}")
                return True, info["title"], filename
        except Exception as e:
            return False, str(e), None

    def download_playlist(
        self,
        _url,
        _type="video",
        _quality="best",
        _audio_format="mp3",
        _progress=None,
        _status=None,
    ):
        """Download entire playlist."""

        def hook(d):
            percentage = d["downloaded_bytes"] / d["total_bytes"]
            if _progress:
                _progress.progress(percentage)
            if _status:
                file_name = d["filename"]
                file_name = (file_name[:30] + "…") if len(file_name) > 30 else file_name
                _status.info(f"{d['status']}: {file_name} - {percentage * 100:.0f}%")

        if _type == "video":
            ydl_opts = {
                "format": (
                    "bestvideo+bestaudio/best"
                    if _quality == "best"
                    else f"bestvideo[height<={_quality[:-1]}]+bestaudio/best"
                ),
                "outtmpl": str(
                    self.download_path
                    / "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
                ),
                "merge_output_format": "mp4",
                "ignoreerrors": True,  # Continue on errors
                "progress_hooks": [hook],
            }
        else:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": str(
                    self.download_path
                    / "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
                ),
                "ffmpeg_location": self.BUNDLED_FFMPEG,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": _audio_format,
                        "preferredquality": "192",
                    }
                ],
                "ignoreerrors": True,
                "progress_hooks": [hook],
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(_url, download=True)
                playlist_title = info.get("title", "playlist")
                video_count = len(info.get("entries", []))
                playlist_folder = self.download_path / playlist_title
                return True, playlist_title, video_count, str(playlist_folder)
        except Exception as e:
            return False, str(e), 0, None

    def create_zip(self, folder_path, zip_name):
        """Create a zip file from a folder."""
        zip_path = self.download_path / f"{zip_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            folder = Path(folder_path)
            for file in folder.rglob("*"):
                if file.is_file():
                    zipf.write(file, file.relative_to(folder.parent))
        return str(zip_path)
