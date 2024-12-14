# ObsidianScrobbleSync

A Python script to fetch your Last.fm scrobbling history and generate Markdown notes and CSV files. 
Integrating with Obsidian for managing daily music history locally.

---

![DailyNote](images\DailyNote.png)

---

## Features

- Fetch recent scrobbles from Last.fm within a customizable time range.
- Save scrobbles to a CSV file for analysis.
- Automatically generate Markdown notes grouped by date for integration with Obsidian.
- Support for "Now Playing" tracks.

---

## Requirements

- Python 3.8 or higher
- A Last.fm **API key** and **shared secret**. 
   Create one [here](https://www.last.fm/api/account/create).
   
   You need to fill out at minimum:
   
      - Contact email
      - Application name
      - Application description
   
   You don't need to input a `callback url`, or a `application homepage` using it in Python like this.
   According to Last.fm docs:
   
   > "When using our web-based authentication this callback URL is sent authentication tokens (more info). 
   > This field isn't used for **desktop** or mobile authentication."

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/arcticpinecone/ObsidianScrobbleSync.git
   cd ObsidianScrobbleSync
   ```

2. Install dependencies:
   ```bash
   pip install requests python-dotenv
   ```

Before proceeding with this info, you need to create the API access. 
Did you read # Requirements? 🤨

3. Create a `.env` file in the ObsidianScrobbleSync directory:

   Add the following to the `.env` file:
   ```.env
   LASTFM_API_KEY=your_api_key_here
   LASTFM_SHARED_SECRET=your_shared_secret_here
   LASTFM_USERNAME=your_lastfm_username_here
   LASTFM_USERAGENT="ObsidianScrobbleSync/1.0 (Contact: you@domain.we)"
   OUTPUT_CSV="lastfm_history.csv"
   OBSIDIAN_PATH="C:/path/to/your/Obsidian/Vault/Music/Last.fm History/or/something"

   ```
   Example:
   ```.env
   LASTFM_API_KEY=F2A3790FE278F78C5F5DF7048F5D8031
   LASTFM_SHARED_SECRET=0C1EF09B2596E114CB730FED02BB99E0
   LASTFM_USERNAME=wrongpalate
   LASTFM_USERAGENT="ObsidianScrobbleSync/1.0 (Contact: arcticpinecone)"
   OUTPUT_CSV="lastfm_history.csv"
   OBSIDIAN_PATH="C:/Users/user/ObsidianVault/Music/Last.fm History"
   ```
   No those don't work, and yes thems mah tunes; 
   Don't judge, from nostalgia to memories of events, places, and people.
   Music is personal. 😿

4. Edit the configuration variables in `ObsidianScrobbleSync.py` to suit your setup:
   - `OUTPUT_CSV`: Path for the CSV output file.
   - `OBSIDIAN_FOLDER`: Path to your Obsidian vault folder.
   - `get_note_path`: Customize the note structure as needed.

💡 Note that 2 files are possibly created: 
   - LastFM_NowPlaying.md which defaults to your OBSIDIAN_PATH. 
      **THIS IS ONLY CREATED/OVERWRITTEN IF YOU ARE CURRENTLY PLAYING SOMETHING.**

   - LastFM_2024-12-14.md which is the daily snapshot file for your 
      This will be created based on the data from Last.fm, up to the most recent full scrobble and doesn't include the now playing track.

---
## Obsidian Template

If you use a daily note, I made this for my template:
```markdown
## Last.fm

> [!info]+ Now Playing via Last.fm
> ![[LastFM_NowPlaying]]

> [!info]- Today's music via Last.fm
![[LastFM_{{date:YYYY/MM/DD}}]]
```
This will populate the note data if the file exists!

---
## Configuration

### Customizing the Date Range

To customize the time range for fetching scrobbles, open ObsidianScrobbleSync.py and locate the following code in the main() function:
```python
to_time = int(datetime.now().timestamp())
from_time = int((datetime.now() - timedelta(days=1)).timestamp())
```

Modify the `timedelta(days=1)` to the desired range. 

For example, to fetch data from the last 7 days:
```python
from_time = int((datetime.now() - timedelta(days=7)).timestamp())
```
To fetch data from a specific date range, replace from_time and to_time with UNIX timestamps. For example:
```python
from_time = int(datetime(2024, 1, 1, 0, 0).timestamp())  # From January 1, 2024
to_time = int(datetime(2024, 1, 7, 23, 59).timestamp())  # To January 7, 2024
```
Save the file and run the script. The scrobbles from the specified range will be fetched.


### Customizing the Destination for Markdown Files

To adjust where the `LastFM_YYYY-MM-DD.md` files are saved and modify their organization:

1. Open the `get_note_path` function in `ObsidianScrobbleSync.py`:
```python
def get_note_path(base_folder, date_str, structure="{year}/{month}/LastFM_{date}.md"):
   ...
```

2. The current default structure groups notes by **Year** and **Month** folders:

```python
structure = "{year}/{month}/LastFM_{date}.md"
```
- This saves the notes in folders like:
```
2024/
   12/
      LastFM_2024-12-14.md
```

#### 3. **Adding Week Organization**:

To group notes by year, week number, and then save the notes by day, you can modify the structure to include `{week}`:
```python
structure = "{year}/Week_{week}/LastFM_{date}.md"
```
This would save the notes in folders like:
```
2024/
   Week_50/
      LastFM_2024-12-14.md
```

To use this structure, make sure to add the `{week}` field in the function:
```python
date_obj = datetime.strptime(date_str, "%Y-%m-%d") if date_str != "Today" else datetime.now()
year = date_obj.strftime("%Y")
month = date_obj.strftime("%m")
week = date_obj.strftime("%U")  # Week number of the year (00–53)
day = date_obj.strftime("%d")
path = structure.format(year=year, month=month, week=week, day=day, date=date_str)
```

#### 4. **Flat Organization**:

If you want all files to go into a single folder without subdirectories, adjust the structure to:
```python
structure = "LastFM_{date}.md"
```

5. Update the `OBSIDIAN_FOLDER` variable to set the base folder for saving the files:
```python
OBSIDIAN_FOLDER = "C:/Path/To/Your/Obsidian/Vault/LastFM"
```

6. Save the script and run it. The Markdown files will now follow your customized folder and filename structure.

### Customizing output files (.md)

You can find this under the function for `generate_markdown_from_csv_grouped`.
The `Now Playing` is commented: `# Write "Now Playing" file if any track is found`
The `Date` file is commented: `# Write scrobble history files`

As an example, I use the following file properties, which help to find and organize them, and get quick info from them:
```markdown
---
noteid: "[[LastFM_2024-12-14]]"
iso8601time: "2024-12-14T18:14:16"
notetype: "[[LastFM]]"
tags:
  - LastFM
  - Scrobble
---
```

These are not necessary, and you can remove the whole --- section --- if you prefer.

---
## Usage

1. Run the script:
   ```bash
   python ObsidianScrobbleSync.py
   ```

2. The script will:
   - Fetch your Last.fm scrobbling history.
   - Save the scrobbles to `lastfm_history.csv`.
   - Generate Markdown files in the configured `OBSIDIAN_FOLDER`.

3. Check for your "Now Playing" or daily scrobble notes in the appropriate subfolder of your Obsidian vault.

---

## Creating a Last.fm API Key

1. Go to the [Last.fm API account creation page](https://www.last.fm/api/account/create).
2. Fill in the required fields:
   - **Contact email**: Your email address.
   - **Application name**: A descriptive name for your app (e.g., ObsidianScrobbleSync).
   - **Application description**: Briefly describe your application.
3. Leave the **Callback URL** field blank. This field isn't used for Python-based desktop authentication.

---

## .gitignore

Ensure you add the following to `.gitignore` to prevent sensitive information and output files from being committed:

```
.env
lastfm_history.csv

```

---

## Troubleshooting

- If you encounter issues with API authentication, double-check your API key, shared secret, and username in the `.env` file.
- For HTTP errors, check the response content for additional details.

### Example Python output

```
ObsidianScrobbleSync.py
Fetching Last.fm history...
Saving data to lastfm_history.csv...
Generating Markdown files in C:/Users/user/ObsidianVault/Entertainment/Music/Last.fm History...
Now Playing Tracks: [{'Artist': 'David Bowie', 'Track': 'Moonage Daydream (2012 Remaster)', 'Album': 'The Rise and Fall of Ziggy Stardust and the Spiders from Mars (2012 Remaster)', 'Timestamp': 'Now Playing'}]
Writing 'Now Playing' file...
Process completed successfully.
```

---

## Attribution

Thank you [@drushadrusha](https://gist.github.com/drushadrusha) for [drushadrusha/obsidian_lastfm.php](https://gist.github.com/drushadrusha/de50a8b67b164326f381184a4000340c), 
and subsequently
Thank you [@benfoxall](https://github.com/benfoxall) for [lastfm-to-csv](https://github.com/benfoxall/lastfm-to-csv)

And of course, should mention the help of the [Last.fm API docs](https://www.last.fm/api).

---

## Contact

For support or feedback, please use the [Issues](https://github.com/arcticpinecone/ObsidianScrobbleSync/issues) section.
