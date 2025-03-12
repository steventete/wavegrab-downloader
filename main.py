import os
import yt_dlp


def create_artist_folder(artist_name: str) -> str:
    """
    Creates and returns the folder path for the artist inside the Downloads/Wavegrab Downloads folder.
    """
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    base_folder = os.path.join(downloads_dir, "Wavegrab Downloads")
    os.makedirs(base_folder, exist_ok=True)

    # Create a folder for the artist within the base folder
    artist_folder = os.path.join(base_folder, artist_name.replace(" ", "_"))
    os.makedirs(artist_folder, exist_ok=True)
    return artist_folder


def build_search_query(artist_name: str, max_videos: int) -> str:
    """
    Constructs the YouTube search query for the artist.
    """
    query = f"{artist_name} songs"
    return f"ytsearch{max_videos}:{query}"


def build_ydl_options(folder: str) -> dict:
    """
    Builds the options dictionary for yt_dlp.
    """
    # Get the absolute path of the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the FFmpeg path relative to the script directory.
    # Adjust to 'ffmpeg/bin' if your executables are inside a bin folder.
    ffmpeg_path = os.path.join(script_dir, 'ffmpeg', 'bin')
    
    return {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "ffmpeg_location": ffmpeg_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }
        ],
        "noplaylist": True,
    }


def download_music(urls: list, ydl_options: dict) -> None:
    """
    Downloads music using yt_dlp with the given list of video URLs and options.
    """
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.download(urls)


def file_exists_for_song(title: str, folder: str) -> bool:
    """
    Returns True if an MP3 file for the given song title exists in the folder.
    """
    # Construct the expected file path for the song (assuming postprocessing yields .mp3)
    file_path = os.path.join(folder, f"{title}.mp3")
    return os.path.exists(file_path)


def main() -> None:
    """
    Main function that orchestrates the download of an artist's songs based on user input.
    It checks for duplicates before downloading.
    """
    artist_name = input("Enter the artist name: ")
    
    try:
        max_videos = int(input("Enter the number of videos to search (e.g., 10): "))
    except ValueError:
        print("Invalid input for number of videos. Defaulting to 10.")
        max_videos = 10

    folder = create_artist_folder(artist_name)
    query_url = build_search_query(artist_name, max_videos)
    ydl_options = build_ydl_options(folder)

    # Extract video info without downloading
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(query_url, download=False)

    entries = info.get("entries", [])
    filtered_urls = []

    for video in entries:
        title = video.get("title", "unknown").strip()
        # If a file for this song already exists, skip it
        if file_exists_for_song(title, folder):
            print(f"Skipping duplicate: {title}")
        else:
            filtered_urls.append(video["webpage_url"])

    if filtered_urls:
        download_music(filtered_urls, ydl_options)
        print(f"✅ Download complete. The songs are in the folder: {folder}")
    else:
        print("No new songs to download.")


if __name__ == "__main__":
    main()
