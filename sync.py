from gmusicapi import Mobileclient 
import io
import os
import logging
import datetime
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

# Initialize and log in
#
# For this to work, `export GM_EMAIL=<your email address>` and
#   `export GM_PASSWORD=<your application specific password>`
mc = Mobileclient()
logging.info("Logging into google music")
result = mc.login(os.environ['GM_EMAIL'], os.environ['GM_PASSWORD'], Mobileclient.FROM_MAC_ADDRESS)
logging.info("Done logging in; result: %s", result)
assert mc.is_authenticated()
assert mc.is_subscribed

# Read the bands from disk
bands = []
with io.open("bandnames.csv", 'r', encoding='utf-8') as f:
  bands = f.readlines()
bands = [band.strip() for band in bands]

# Search for each of the band names, recording the store id of the top song result in each
# set of search results.
store_track_ids = []
for band in bands:
  results = mc.search(band)
  if 'song_hits' not in results or len(results['song_hits']) == 0:
    logging.error("No song results for query '%s'", band)
    continue

  song = results['song_hits'][0]
  logging.info("For band '%s', got song %s", band, song)

  store_track_ids.append(song['track']['storeId'])

# Add each of those songs to the library, so that we can transform the store song ids into
# song ids. Why doesn't the search result return song ids? Who knows.
logging.info("Adding store tracks to library")
track_ids = mc.add_store_tracks(store_track_ids)

# Create a new playlist.
logging.info("Creating new playlist")
playlist_id = mc.create_playlist("Iceland Airwaves 2017 - %s" % unicode(datetime.datetime.now()),
                                 "The top song result for each band name in the Iceland Airwaves lineup",
                                 public=True)
logging.info("Created playlist with id %s", playlist_id)

# Add all of the song ids to the newly-created playlist.
logging.info("Adding song ids to playlist")
mc.add_songs_to_playlist(playlist_id, track_ids)
