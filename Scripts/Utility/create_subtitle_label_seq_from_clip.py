#!/usr/bin/env python


"""
Creates individual timelines for each clip in a directory conformed to the clip
properties.
"""

import os

manager = resolve.GetProjectManager()
project = manager.GetCurrentProject()
pool = project.GetMediaPool()
folder = pool.GetCurrentFolder()

for clip in folder.GetClipList():
    name = os.path.splitext(clip.GetClipProperty("Clip Name"))[0]
    start = clip.GetClipProperty("Start TC")
    fps = clip.GetClipProperty("FPS")
    resolution = clip.GetClipProperty("Resolution")
    width, height = resolution.split("x")
    drop_frame = clip.GetClipProperty("Drop frame")
    timeline = pool.CreateEmptyTimeline(name)
    timeline.SetSetting("useCustomSettings", "1")
    timeline.SetSetting("timelineFrameRate", fps)
    timeline.SetSetting("timelineDropFrameTimecode", drop_frame)
    timeline.SetSetting("timelineResolutionHeight", height)
    timeline.SetSetting("timelineResolutionWidth", width)
    timeline.SetStartTimecode(start)
    pool.AppendToTimeline(clip)
    timeline.AddTrack("subtitle")
