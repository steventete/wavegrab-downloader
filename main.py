import os
import yt_dlp
from pyfiglet import figlet_format


def progress_hook(d):
    """
    Displays simple progress messages based on the download process.
    """
    status = d.get("status")
    if status == "downloading":
        print(f"Downloading: {d.get('filename', 'unknown')}", end="\r")
    elif status == "finished":
        print(f"\nFinished downloading: {d.get('filename', 'unknown')}")
    elif status == "postprocessing":
        print(f"Extracting audio for: {d.get('filename', 'unknown')}")


def create_artist_folder(artist_name: str) -> str:
    """
    Creates and returns the folder path for the given name inside the Downloads/Wavegrab Downloads folder.
    """
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    base_folder = os.path.join(downloads_dir, "Wavegrab Downloads")
    os.makedirs(base_folder, exist_ok=True)

    # Folder name is based on the given artist/genre name (spaces replaced with underscores)
    target_folder = os.path.join(base_folder, artist_name.replace(" ", "_"))
    os.makedirs(target_folder, exist_ok=True)
    return target_folder


def build_search_query(query_term: str, max_videos: int) -> str:
    """
    Constructs the YouTube search query based on the given term.
    """
    query = f"{query_term} songs"
    return f"ytsearch{max_videos}:{query}"


def build_ydl_options(folder: str) -> dict:
    """
    Builds the yt_dlp options dictionary.
    """
    # Get the absolute path of the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust this if your FFmpeg executables are located in a different subfolder.
    ffmpeg_path = os.path.join(script_dir, "ffmpeg", "bin")
    
    return {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "ffmpeg_location": ffmpeg_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "noplaylist": True,
        "quiet": True,  # Suppress yt_dlp internal logs.
        "progress_hooks": [progress_hook],
    }


def download_music(urls: list, ydl_options: dict) -> None:
    """
    Downloads media using yt_dlp with the provided list of URLs and options.
    """
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.download(urls)


def file_exists_for_song(title: str, folder: str) -> bool:
    """
    Returns True if an MP3 file for the given song title already exists in the folder.
    """
    file_path = os.path.join(folder, f"{title}.mp3")
    return os.path.exists(file_path)


def download_single_song():
    """
    Downloads a single song from a YouTube link.
    """
    link = input("Enter the YouTube link for the song: ").strip()
    folder = create_artist_folder("Single_Songs")
    ydl_options = build_ydl_options(folder)
    ydl_options["noplaylist"] = True  # Ensure single video mode.
    download_music([link], ydl_options)
    print(f"\n✅ Download complete. The song is saved in: {folder}")


def download_playlist():
    """
    Downloads an entire playlist from a YouTube link.
    """
    link = input("Enter the YouTube playlist link: ").strip()
    folder = create_artist_folder("Playlists")
    ydl_options = build_ydl_options(folder)
    ydl_options["noplaylist"] = False  # Enable playlist download.
    download_music([link], ydl_options)
    print(f"\n✅ Download complete. The playlist is saved in: {folder}")


def download_artist_music():
    """
    Searches and downloads a specific number of songs by artist,
    avoiding duplicates based on file existence.
    """
    artist = input("Enter the artist name: ").strip()
    try:
        max_videos = int(input("Enter the number of videos to search (e.g., 10): "))
    except ValueError:
        print("Invalid input. Defaulting to 10 videos.")
        max_videos = 10

    folder = create_artist_folder(artist)
    query_url = build_search_query(artist, max_videos)
    ydl_options = build_ydl_options(folder)

    print("Fetching video info...")
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(query_url, download=False)
    entries = info.get("entries", [])
    filtered_urls = []
    print("Filtering duplicate songs...")
    for video in entries:
        title = video.get("title", "unknown").strip()
        if file_exists_for_song(title, folder):
            print(f"Skipping duplicate: {title}")
        else:
            filtered_urls.append(video["webpage_url"])

    if filtered_urls:
        download_music(filtered_urls, ydl_options)
        print(f"\n✅ Download complete. The songs are saved in: {folder}")
    else:
        print("No new songs to download.")


def download_genre_music():
    """
    Searches and downloads a specific number of songs by genre,
    avoiding duplicates based on file existence.
    """
    genre = input("Enter the music genre: ").strip()
    try:
        max_videos = int(input("Enter the number of videos to search (e.g., 10): "))
    except ValueError:
        print("Invalid input. Defaulting to 10 videos.")
        max_videos = 10

    folder = create_artist_folder(genre)
    query_url = build_search_query(genre, max_videos)
    ydl_options = build_ydl_options(folder)

    print("Fetching video info...")
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(query_url, download=False)
    entries = info.get("entries", [])
    filtered_urls = []
    print("Filtering duplicate songs...")
    for video in entries:
        title = video.get("title", "unknown").strip()
        if file_exists_for_song(title, folder):
            print(f"Skipping duplicate: {title}")
        else:
            filtered_urls.append(video["webpage_url"])

    if filtered_urls:
        download_music(filtered_urls, ydl_options)
        print(f"\n✅ Download complete. The songs are saved in: {folder}")
    else:
        print("No new songs to download.")


def display_menu():
    """
    Displays a pretty ASCII banner and menu options.
    """
    banner = figlet_format("Wavegrab", font="slant")
    print(banner)
    print("Welcome to Wavegrab Downloader")
    print("GitHub: https://github.com/steventete/wavegrab-downloader")
    print("\nSelect an option:")
    print("1. Download a single song (YouTube link)")
    print("2. Download a playlist (YouTube link)")
    print("3. Download music by artist")
    print("4. Download music by genre")
    print("5. Exit")


def main_menu():
    """
    Main menu loop.
    """
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            download_single_song()
        elif choice == "2":
            download_playlist()
        elif choice == "3":
            download_artist_music()
        elif choice == "4":
            download_genre_music()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        input("Press Enter to continue...")


if __name__ == "__main__":
    main_menu()
