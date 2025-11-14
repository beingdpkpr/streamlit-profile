import streamlit as st
import yt_dlp
import os
from pathlib import Path
import zipfile

st.title("📜 Youtube Downloader")


class YouTubeDownloader:
    def __init__(self, download_path="downloads"):
        """Initialize downloader with a download directory."""
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)

    def progress_hook(self, d, _progress_bar=None, _status_text=None):
        """Hook for download progress."""
        if d["status"] == "downloading":
            if _progress_bar and "downloaded_bytes" in d and "total_bytes" in d:
                percent = d["downloaded_bytes"] / d["total_bytes"]
                _progress_bar.progress(percent)
            if _status_text:
                _status_text.text(
                    f"Downloading: {d.get('_percent_str', 'N/A')} at {d.get('_speed_str', 'N/A')}"
                )
        elif d["status"] == "finished":
            if _status_text:
                _status_text.text("Download complete, processing...")

    def download_video(self, _url, _quality="best", bar=None, status=None):

        def hook(d):
            percentage = d["downloaded_bytes"] / d["total_bytes"]
            if bar is not None:
                bar.progress(percentage)
            if status:
                status.info(f"{d['status']} - {percentage * 100:.2f}%")

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

    def download_audio(self, url, format="mp3", bar=None, status=None):
        """Download only audio from video."""

        def hook(d):
            percentage = d["downloaded_bytes"] / d["total_bytes"]
            if bar is not None:
                bar.progress(percentage)
            if status:
                status.info(f"{d['status']} - {percentage * 100:.2f}%")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(self.download_path / "%(title)s.%(ext)s"),
            "ffmpeg_location": r"C:\ffmpeg\bin",  # <-- adjust if needed
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": format,
                    "preferredquality": "192",
                }
            ],
            "progress_hooks": [hook],
        }
        try:
            # print(f"Downloading Audio: {self.download_path}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = str(self.download_path / f"{info['title']}.{format}")
                return True, info["title"], filename
        except Exception as e:
            return False, str(e), None

    def download_playlist(
        self, url, download_type="video", quality="best", audio_format="mp3"
    ):
        ffmpeg_path = r"C:\ffmpeg\bin"
        """Download entire playlist."""
        if download_type == "video":
            ydl_opts = {
                "format": (
                    "bestvideo+bestaudio/best"
                    if quality == "best"
                    else f"bestvideo[height<={quality[:-1]}]+bestaudio/best"
                ),
                "outtmpl": str(
                    self.download_path
                    / "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
                ),
                "merge_output_format": "mp4",
                "ignoreerrors": True,  # Continue on errors
            }
        else:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": str(
                    self.download_path
                    / "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
                ),
                "ffmpeg_location": ffmpeg_path,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": audio_format,
                        "preferredquality": "192",
                    }
                ],
                "ignoreerrors": True,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
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
            f"⬇️ Download {download_type}", type="primary", use_container_width=True
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

            def update_progress(pct, message):
                progress_bar.progress(pct / 100)  # correct scale
                status_text.text(message)

            status_text.text("Starting download...")

            if download_type == "Video":
                success, result, filename = downloader.download_video(
                    url, quality, progress_bar, status_text
                )
            else:
                success, result, filename = downloader.download_audio(
                    url, audio_format, progress_bar, status_text
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
            # Playlist download
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Starting playlist download... This may take a while.")
            progress_bar.progress(10)

            if download_type == "Video":
                success, result, count, folder = downloader.download_playlist(
                    url, "video", quality
                )
            else:
                success, result, count, folder = downloader.download_playlist(
                    url, "audio", audio_format=audio_format
                )

            progress_bar.progress(90)

            if success:
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
