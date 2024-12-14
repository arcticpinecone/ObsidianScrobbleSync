import requests
import csv
import hashlib
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from collections import defaultdict

# Load environment variables from .env file
load_dotenv()

# Configuration
API_KEY = os.getenv("LASTFM_API_KEY")
SHARED_SECRET = os.getenv("LASTFM_SHARED_SECRET")
USERNAME = os.getenv("LASTFM_USERNAME")
USER_AGENT = "ScrobbleSync/1.0 (Contact: your-last-fm-email@address.com)"
OUTPUT_CSV = "lastfm_history.csv"
OBSIDIAN_FOLDER = "C:/Users/user/ObsidianVault/Entertainment/Music/Last.fm History"


# Path customization function
def get_note_path(base_folder, date_str, structure="{year}/{month}/LastFM_{date}.md"):
    """Generate the file path for the note based on the date and user-defined structure."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d") if date_str != "Today" else datetime.now()
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    day = date_obj.strftime("%d")
    path = structure.format(year=year, month=month, day=day, date=date_str)
    return os.path.join(base_folder, path)

# Helper Functions
def generate_api_signature(params):
    """Generate an API signature using the shared secret."""
    # Exclude 'format' and 'callback' from signature generation
    params_to_sign = {k: v for k, v in params.items() if k not in ["format", "callback"]}
    sorted_params = ''.join(f"{key}{value}" for key, value in sorted(params_to_sign.items()))
    hash_string = sorted_params + SHARED_SECRET
    return hashlib.md5(hash_string.encode('utf-8')).hexdigest()

def fetch_lastfm_history(from_timestamp, to_timestamp, limit=200):
    """Fetch recent tracks from Last.fm within a specified time range."""
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": USERNAME,
        "api_key": API_KEY,
        "from": from_timestamp,
        "to": to_timestamp,
        "limit": limit,
        "format": "json"
    }
    params["api_sig"] = generate_api_signature(params)
    headers = {
        "User-Agent": USER_AGENT
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        print(f"Response content: {response.text}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def parse_tracks_to_csv(tracks, output_file):
    """Parse tracks into a CSV file."""
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Artist", "Track", "Album", "Timestamp"])
        for track in tracks:
            artist = track["artist"]["#text"]
            track_name = track["name"]
            album = track.get("album", {}).get("#text", "Unknown Album")
            timestamp = track["date"]["uts"] if "date" in track else "Now Playing"
            writer.writerow([artist, track_name, album, timestamp])

def generate_markdown_from_csv_grouped(csv_file, obsidian_folder, structure="{year}/{month}/LastFM_{date}.md"):
    """Generate grouped Markdown tables by date from CSV."""
    grouped_data = defaultdict(list)
    now_playing = []

    with open(csv_file, mode="r", encoding="utf-8") as csv_file_handle:
        reader = csv.DictReader(csv_file_handle)
        for row in reader:
            timestamp = datetime.fromtimestamp(int(row["Timestamp"]), timezone.utc) if row["Timestamp"].isdigit() else "Now Playing"
            date_str = timestamp.strftime("%Y-%m-%d") if timestamp != "Now Playing" else "Today"
            if date_str == "Today":
                now_playing.append(row)
            else:
                grouped_data[date_str].append(row)

    # Debugging: Check if now_playing has entries
    print(f"Now Playing Tracks: {now_playing}")

    # Write "Now Playing" file if any track is found
    if now_playing:
        print("Writing 'Now Playing' file...")
        markdown_file = os.path.join(obsidian_folder, "LastFM_NowPlaying.md")
        os.makedirs(os.path.dirname(markdown_file), exist_ok=True)
        with open(markdown_file, mode="w", encoding="utf-8") as md_file:
            # YAML Frontmatter
            iso8601time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
            md_file.write("---\n")
            md_file.write(f"noteid: \"[[NowPlaying]]\"\n")
            md_file.write(f"iso8601time: \"{iso8601time}\"\n")
            md_file.write("notetype: \"[[LastFM]]\"\n")
            md_file.write("tags:\n")
            md_file.write("  - LastFM\n")
            md_file.write("  - NowPlaying\n")
            md_file.write("---\n\n")

            # Markdown Content
            md_file.write("# Last.fm - Now Playing\n\n")
            md_file.write("| Track | Artist | Album | Timestamp |\n")
            md_file.write("|-------|--------|-------|-----------|\n")
            for track in now_playing:
                md_file.write(f"| **{track['Track']}** | *{track['Artist']}* | {track['Album']} | {iso8601time} |\n")
    else:
        print("No 'Now Playing' tracks found.")

    # Write scrobble history files
    for date, tracks in grouped_data.items():
        # Sort tracks by timestamp in ascending order
        sorted_tracks = sorted(tracks, key=lambda x: int(x["Timestamp"]) if x["Timestamp"].isdigit() else 0)
        markdown_file = get_note_path(obsidian_folder, date, structure)
        os.makedirs(os.path.dirname(markdown_file), exist_ok=True)

        with open(markdown_file, mode="w", encoding="utf-8") as md_file:
            # YAML frontmatter
            noteid = f"[[LastFM_{date}]]"
            iso8601time = f"{date}T{datetime.now(timezone.utc).strftime('%H:%M:%S')}"
            md_file.write("---\n")
            md_file.write(f"noteid: \"{noteid}\"\n")
            md_file.write(f"iso8601time: \"{iso8601time}\"\n")
            md_file.write("notetype: \"[[LastFM]]\"\n")
            md_file.write("tags:\n")
            md_file.write("  - LastFM\n")
            md_file.write("  - Scrobble\n")
            md_file.write("---\n\n")

            # Header for scrobble history
            md_file.write(f"# Last.fm - Scrobble History ({date})\n\n")
            md_file.write("| Track | Artist | Album | Timestamp |\n")
            md_file.write("|-------|--------|-------|-----------|\n")
            for track in sorted_tracks:
                timestamp = datetime.fromtimestamp(int(track["Timestamp"]), timezone.utc).strftime("%H:%M:%S")
                md_file.write(f"| **{track['Track']}** | *{track['Artist']}* | {track['Album']} | {timestamp} |\n")

# Main Functionality
def main():
    # Adjust time range here
    to_time = int(datetime.now().timestamp())
    from_time = int((datetime.now() - timedelta(days=1)).timestamp())

    # Fetch data
    print("Fetching Last.fm history...")
    data = fetch_lastfm_history(from_time, to_time)

    if not data:
        print("Failed to fetch data. Please check logs for details.")
        return

    # Parse tracks
    tracks = data.get("recenttracks", {}).get("track", [])
    if not tracks:
        print("No tracks found in the specified time range.")
        return

    # Save to CSV
    print(f"Saving data to {OUTPUT_CSV}...")
    parse_tracks_to_csv(tracks, OUTPUT_CSV)

    # Generate Obsidian Markdown with grouped table
    print(f"Generating Markdown files in {OBSIDIAN_FOLDER}...")
    generate_markdown_from_csv_grouped(OUTPUT_CSV, OBSIDIAN_FOLDER)

    print("Process completed successfully.")

if __name__ == "__main__":
    main()
