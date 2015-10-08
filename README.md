# Automatic Video Converter

Converts videos given on stdin to a smaller version. Uses the H.264 codec to do that. Also, it ignores video files that have been converted already.

This is great in combination with a file change monitor, i.e. [fswatch](https://github.com/emcrisostomo/fswatch).

## Installation

```
sudo pip install --upgrade git+https://github.com/resamsel/auto-video-converter.git#egg=auto-video-converter
```

## Example Usage

Uses **fswatch** to monitor file changes in the photos library. With every import of a video into the Mac Photos app, avconv will try to determine whether or not this video file needs a conversion. This command can be started as a background process.

```
fswatch ~/Pictures/Photos\ Library.photoslibrary | avconv
```

## Next

* Configuration (codec, conversion determination, ...)
* Requirements through setup.py (https://github.com/senko/python-video-converter)
