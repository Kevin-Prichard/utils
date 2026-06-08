#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from collections import defaultdict as dd
from datetime import datetime as dt
import json
import logging
import os
from pathlib import Path
import sys
from typing import List, Dict, Text

from box import Box
import filedate
import jq
import regex

import pudb

to_yyyymmdd = lambda ts: dt.fromtimestamp(ts).strftime("%Y%m%d")

logger = logging.getLogger(__name__)

MEDIA_RX = regex.compile(r"(?P<basename>.+\[(?P<media_id>[^\]]+)\]\.?\w*)"
                         r"\.(?P<filetype>webm|mp4|mkv)$")

FILESYS_UNSAFE_RX = regex.compile(r"[<>:\"/\\|?*\x00-\x1F]")


def get_args(args):
    parser = argparse.ArgumentParser(
        description="Index and organize YouTube media files based on "
                    "associated metadata JSON files."
    )
    parser.add_argument(
        '-r', '--read-cache', type=Path, default=None,
        help="Path to a previously generated cache JSON file to read and use "
             "instead of scanning directories. This can speed up processing."
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="One or more directory paths to scan for media and metadata files."
    )
    return parser.parse_args(args)


def slurp(paths: List[Text]) -> Dict[Text, Dict]:
    file_count, info_count, media_count = 0, 0, 0

    # filenames -> [path, ...]
    media2video = dd(list)

    # full_path -> {ctime: created time, mtime: modified time}
    pathTimes = dict()

    # channel IDs -> [path, ...]
    chan2media = dd(list)

    # media IDs -> channel IDs
    media2chan = dict()

    # chan IDs -> chan info
    chaninfos = dict()

    # chan IDs -> {minDlTime, maxDlTime, minPubTime, maxPubTime}
    chanMeta = dict()

    # media IDs -> {channel, channel_id, channel_url, description, channel_follower_count,
    mediaMeta = dict()

    for path in paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                path_stat = os.stat(full_path)
                # pathTimes[full_path] = {
                #     "ctime": path_stat.st_ctime,
                #     "mtime": path_stat.st_mtime,
                # }
                thems = [getattr(path_stat, t)
                         for t in ['st_atime', 'st_mtime', 'st_ctime']]
                spread = [min(thems), max(thems)]
                if ".chandex-cache" in full_path:
                    continue
                extension = file.lower().split(".")[-1]
                if extension == "json":
                    with open(full_path, "rb") as f:
                        try:
                            jsonbody = f.read().decode("utf-8")
                            if "youtube" not in jsonbody:
                                continue
                            chaninfo = (jq.compile(
                                 "pick(.channel, .channel_id, .channel_url, "
                                 ".description, .channel_follower_count, .id, "
                                 ".epoch, .upload_date, .title)")
                            ).input_text(jsonbody).first()

                            upload_ts = dt.strptime(
                                chaninfo.get("upload_date", "19700101")[:8],
                                "%Y%m%d").timestamp()

                            download_ts = to_yyyymmdd(
                                    chaninfo.get("epoch", 0))

                            mediaMeta[chaninfo['id']] = {
                                "upload": to_yyyymmdd(upload_ts),
                                "download": download_ts,
                            }
                            # print(chaninfo.get("upload_date", "--------"), "\t",
                            #       download_ts, "***")

                            thisMeta = chanMeta.get(chaninfo["channel_id"], {
                                "minDlTime": float("inf"),
                                "maxDlTime": 0,
                                "minPubDate": float("inf"),
                                "maxPubDate": 0,
                            })
                            thisMeta["minDlTime"] = min(
                                thisMeta["minDlTime"],
                                chaninfo.get("epoch", float("inf")))
                            thisMeta["maxDlTime"] = max(
                                thisMeta["maxDlTime"],
                                chaninfo.get("epoch", 0))

                            thisMeta["minPubDate"] = min(
                                thisMeta["minPubDate"], upload_ts)
                            thisMeta["maxPubDate"] = max(
                                thisMeta["maxPubDate"], upload_ts)

                            chanMeta[chaninfo["channel_id"]] = thisMeta
                            if "youtube" not in chaninfo["channel_url"]:
                                continue

                            chaninfos[chaninfo["channel_id"]] = chaninfo
                            media2chan[chaninfo["id"]] = chaninfo["channel_id"]

                        except Exception as e:
                            import traceback as tb
                            print(f"Error loading {os.path.join(root, file)}: {e}")
                            tb.print_exc()
                            continue
                    info_count += 1

                elif extension in ["mp4", "webm", "mkv"]:
                    if media_match := MEDIA_RX.match(full_path):
                        media_id = media_match.capturesdict()["media_id"][0]

                        if spread[1] - spread[0] > 86400 * 365.25 and len(
                                media_id) == 11:
                            print(full_path)
                            print(f"  Time spread: "
                                  f"{(spread[1] - spread[0]) / 86400:.1f} "
                                  f"days")
                            times = [
                                (f'{t}: '
                                 f'{dt.fromtimestamp(getattr(path_stat, t)).strftime("%Y/%m/%d")}')
                                  for t in
                                  ['st_atime', 'st_mtime', 'st_ctime']]
                            print(times)

                        media2video[media_id].append(full_path)
                    else:
                        print(f"Could not parse media ID from filename: {full_path}")
                    media_count += 1

                else:
                    print(f"Skipping file with unsupported extension "
                          f"({extension}): {full_path}")

                file_count += 1
                if file_count % 100 == 0:
                    print(f"Processed {file_count} files, info: {info_count}, "
                          f"media: {media_count}")

    for media_id, paths in media2video.items():
        if len(paths) > 1:
            print(f"Media ID {media_id} has multiple paths: {paths}")
        if chan_id := media2chan.get(media_id, None):
            # if chan2media.get(chan_id):
            #     pu.db
            chan2media[chan_id].append((media_id, paths))
        else:
            print(f"No channel ID for media ID {media_id}, paths: {paths}")

    print(f"Processed {file_count} files, info: {info_count}, "
          f"media: {media_count}")
    return Box({
        "chaninfos": chaninfos,
        "media2video": media2video,
        "pathTimes": pathTimes,
        "chan2media": chan2media,
        "media2chan": media2chan,
        "chanMeta": chanMeta,
        "mediaMeta": mediaMeta,
    })


def build_chan_index(inf, where_path):
    existing_symlinks = 0
    new_symlinks = 0
    error_symlinks = 0
    existing_chans = 0
    new_chans = 0
    for chan_id, chaninfo in inf.chaninfos.items():
        try:
            chan_name_safe = FILESYS_UNSAFE_RX.sub("_", chaninfo.channel)
            chan_path = Path(where_path,
                             f"{chan_name_safe} [{chan_id}]")
            print(f"Channel {chan_name_safe} ({chan_id}) -> {chan_path}")
        except Exception as e:
            print(f"Error creating channel path for {chaninfo.channel} "
                  f"({chan_id}): {e}")
            continue

        media_paths = inf.chan2media.get(chan_id, [])
        if not media_paths:
            print(f"No media for channel {chan_id} ({chaninfo.channel})")
            continue

        if chan_path and not chan_path.exists():
            chan_path.mkdir(parents=True, exist_ok=True)
            new_chans += 1
        else:
            existing_chans += 1

        # pu.db
        try:
            for media_id, paths in media_paths:
                for media_path in paths:
                    try:
                        med = Path(media_path).absolute()
                        med_name_safe = FILESYS_UNSAFE_RX.sub("_", med.name)
                        chan_media_path = (chan_path / med_name_safe).absolute()
                        if chan_media_path.exists():
                            if mat := MEDIA_RX.match(chan_media_path.name):
                                for i in range(25):
                                    proposed_name = f"{mat.capturesdict()['basename'][0]}-{i}." \
                                                    f"{mat.capturesdict()['filetype'][0]}"
                                    proposed_path = chan_path / proposed_name
                                    if not proposed_path.exists():
                                        chan_media_path = proposed_path
                                        break
                                    existing_symlinks += 1
                            else:
                                pu.db
                                x = 1

                        print(f"Creating symlink {chan_media_path} -> {med}")
                        chan_media_path.symlink_to(med, target_is_directory=False)
                        mediaChanFile = filedate.File(chan_media_path)
                        mediaChanFile.set(
                            created = inf.mediaMeta[media_id]["upload"],
                            modified = inf.mediaMeta[media_id]["download"],
                            # accessed = inf.mediaMeta[media_id]["download"],
                            #accessed = dt.now().timestamp(),
                        )
                        # print(dt.fromtimestamp(inf.mediaMeta[media_id]["upload"]), "\t",
                        #       dt.fromtimestamp(inf.mediaMeta[media_id]["download"]))
                        mediaFile = filedate.File(med)
                        mediaFile.set(
                            created = inf.mediaMeta[media_id]["upload"],
                            modified = inf.mediaMeta[media_id]["download"],
                            # accessed = inf.mediaMeta[media_id]["download"],
                            #accessed = dt.now().timestamp(),
                        )
                        new_symlinks += 1
                        # pu.db
                        # filedate.File(chan_media_path).set(
                        #     created=inf.mediaMeta[media_id]["upload"],
                        #     modified=inf.mediaMeta[media_id]["download"],
                        #     accessed=dt.now().timestamp(),
                        # )
                    except Exception as e:
                        from traceback import print_exc
                        print_exc()
                        print(f"Error creating symlink for media {media_path}: {e}")
                        error_symlinks += 1
                        pu.db
                        x = 1

            # after all mods to channel dir completed, then update its times
            print(to_yyyymmdd(inf.chanMeta[chan_id]["minPubDate"]), "\t",
                  to_yyyymmdd(inf.chanMeta[chan_id]["maxPubDate"]))

            filedate.File(str(chan_path)).set(
                created=to_yyyymmdd(inf.chanMeta[chan_id]["minPubDate"]),
                modified=to_yyyymmdd(inf.chanMeta[chan_id]["maxPubDate"]),
                # accessed=dt.now().timestamp(),
            )

        except Exception as e:
            pu.db
            x = 1

        # os.utime(chan_path, (
        #     inf.chanMeta[chan_id]["maxPubTime"],  # atime
        #     inf.chanMeta[chan_id]["minPubTime"],  # ctime
        # ), follow_symlinks=False)

    print(f"new_symlinks: {new_symlinks}, "
          f"existing_symlinks: {existing_symlinks}, "
          f"error_symlinks: {error_symlinks}, "
          f"new_chans: {new_chans}, "
          f"existing_chans: {existing_chans}")


if __name__ == '__main__':
    args = get_args(sys.argv[1:])
    if args.read_cache:
        print(f"Reading cache from {args.read_cache}")
        with open(args.read_cache, "rb") as f:
            d = Box(json.loads(f.read().decode("utf-8")))
    else:
        try:
            d = slurp(args.sources)
            with open(f'.chandex-cache/cache-'
                      f'{dt.now().strftime("%Y%m%d-%H%M%S")}.json', "wb") as fh:
                fh.write(json.dumps(d, indent=2).encode("utf-8"))
        except Exception as e:
            print(e)
            pu.db
            x = 1
    build_chan_index(d, os.environ.get('CHANDEX_TARGET', 'chandex'))
