import os

import streamlit as st

from app.youtube_downloader import YouTubeDownloader

st.title("📹 Youtube Downloader")


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
