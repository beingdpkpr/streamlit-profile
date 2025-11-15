import streamlit as st
import yt_dlp
import os
from pathlib import Path
from shutil import which
import zipfile
import platform

st.title("📜 Youtube Downloader")


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


# Initialize downloader
downloader = YouTubeDownloader()

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    content_type = st.radio(
        "Content Type",
        ["Single Video", "Playlist"],
        # ["Playlist", "Single Video"],
        help="Choose to download a single video or entire playlist",
    )
with col2:
    download_type = st.radio(
        "Download Type",
        ["Video", "Audio Only"],
        help="Choose whether to download video or just audio",
    )
with col3:
    if download_type == "Video":
        quality = st.selectbox(
            "Video Quality",
            ["best", "1080p", "720p", "480p", "360p"],
            help="Select video quality",
        )
    else:
        audio_format = st.selectbox(
            "Audio Format",
            ["mp3", "m4a", "wav", "opus"],
            help="Select audio format",
        )
st.markdown("---")
with st.expander(f"Instructions", expanded=False):
    if content_type == "Single Video":
        st.markdown(
            """
        1. Paste a YouTube URL
        2. Select download options
        3. Click Download
        """
        )
    else:
        st.markdown(
            """
        1. Paste a YouTube Playlist URL
        2. Select download options
        3. Click Download Playlist
        4. Wait for all videos to download
        """
        )
st.markdown("---")
st.warning("⚠️ Only download content you have permission to download.")

if content_type == "Single Video":
    url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste the YouTube video URL here",
    )
else:
    url = st.text_input(
        "YouTube Playlist URL",
        placeholder="https://www.youtube.com/playlist?list=...",
        help="Paste the YouTube playlist URL here",
    )

# Download section
st.markdown("---")
download_col1, download_col2, download_col3 = st.columns([1, 1, 1])

with download_col2:
    if content_type == "Single Video":
        download_btn = st.button(
            f"⬇️ Download {download_type}",
            type="primary",
            use_container_width=True,
        )
    else:
        download_btn = st.button(
            f"⬇️ Download Playlist ({download_type})",
            type="primary",
            use_container_width=True,
        )

if download_btn:
    if not url:
        st.error("⚠️ Please enter a YouTube URL first!")
    else:
        if content_type == "Single Video":
            progress_bar = st.progress(0)
            status_text = st.empty()
            # Remove List from URL
            url = url.split("&list")[0]
            status_text.text("Starting download...")

            if download_type == "Video":
                success, result, filename = downloader.download_video(
                    _url=url,
                    _quality=quality,
                    _progress=progress_bar,
                    _status=status_text,
                )
            else:
                success, result, filename = downloader.download_audio(
                    _url=url,
                    _format=audio_format,
                    _progress=progress_bar,
                    _status=status_text,
                )

            progress_bar.progress(100)

            if success:
                status_text.empty()
                st.success(f"✅ Successfully downloaded: **{result}**")
                st.info(f"📁 Saved to: `{filename}`")

                # Provide download button
                if filename and os.path.exists(filename):
                    with open(filename, "rb") as file:
                        btn = st.download_button(
                            label="💾 Download File",
                            data=file,
                            file_name=os.path.basename(filename),
                            mime="application/octet-stream",
                        )
            else:
                status_text.empty()
                st.error(f"❌ Download failed: {result}")
        else:
            header_status = st.empty()
            header_status.text("Downloading Entire Playlist... This may take a while.")

            # Playlist download
            progress_bar = st.progress(0)
            status_text = st.empty()

            if download_type == "Video":
                success, result, count, folder = downloader.download_playlist(
                    _url=url,
                    _type="video",
                    _quality=quality,
                    _progress=progress_bar,
                    _status=status_text,
                )
            else:
                success, result, count, folder = downloader.download_playlist(
                    _url=url,
                    _type="audio",
                    _audio_format=audio_format,
                    _progress=progress_bar,
                    _status=status_text,
                )

            if success:
                header_status.empty()
                progress_bar.progress(100)
                status_text.empty()
                st.success(f"✅ Successfully downloaded playlist: **{result}**")
                st.info(f"📁 Downloaded {count} videos to: `{folder}`")

                # Create zip file
                if folder and os.path.exists(folder):
                    with st.spinner("Creating zip file..."):
                        zip_path = downloader.create_zip(folder, result)

                    if os.path.exists(zip_path):
                        with open(zip_path, "rb") as file:
                            btn = st.download_button(
                                label="📦 Download Playlist as ZIP",
                                data=file,
                                file_name=os.path.basename(zip_path),
                                mime="application/zip",
                            )
            else:
                status_text.empty()
                st.error(f"❌ Playlist download failed: {result}")
