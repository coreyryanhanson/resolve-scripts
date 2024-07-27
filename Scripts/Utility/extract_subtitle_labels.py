#!/usr/bin/env python


"""
Creates a labeling csv from the subtitle track.
"""

import csv
import os

# Set the CSV directory here.
dirpath = ""
os.makedirs(dirpath, exist_ok=True)
# If multiple subtitle tracks, change to the one containing the labels.
subtitle_track = 1

manager = resolve.GetProjectManager()
project = manager.GetCurrentProject()
timeline = project.GetCurrentTimeline()
clipname = timeline.GetItemListInTrack("video", 1)[0].GetName()
offset = timeline.GetStartFrame()

filepath = os.path.join(dirpath, os.path.splitext(clipname)[0] + ".csv")

width = timeline.GetSetting("timelineResolutionWidth")
height = timeline.GetSetting("timelineResolutionHeight")
aspect = int(width) / int(height)

# Open the output file
with open(filepath, "w", newline="") as file:
    writer = csv.writer(file)

    # The column names in order
    header = ["file", "label", "start", "end", "duration", "aspect_ratio"]
    writer.writerow(header)

    for subtitle in timeline.GetItemListInTrack("subtitle", subtitle_track):
        name = subtitle.GetName()
        start = subtitle.GetStart() - offset
        end = subtitle.GetEnd() - offset
        duration = end - start
        writer.writerow([clipname, name, start, end, duration, aspect])
