#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import shutil
import argparse

from converter import Converter

FILE_TYPES = ('.mp4', '.avi', '.mov', '.m4v')
TARGET_CODEC = 'h264'
TODO_ENCODERS = ("'avc1'",)

logger = logging.getLogger(__name__)


def stream(info, type_):
	streams = filter(
		lambda s: s.type == type_,
		info.streams
	)
	if len(streams) > 0:
		return streams[0]
	return None


def check(video):
	"""Checks whether the video needs conversion or not"""

	if video.codec != TARGET_CODEC:
		return True

	if video.metadata.get('encoder', None) in TODO_ENCODERS:
		return True

	return False


def process(source, config):
	logger.debug('Processing %s', source)

	filepath, extension = os.path.splitext(source)
	basename = os.path.basename(source)
	tmpfile = '/tmp/{0}-enc{1}'.format(os.path.basename(filepath), extension)
	if extension.lower() not in FILE_TYPES:
		return

	c = Converter(
		ffmpeg_path='/usr/local/bin/ffmpeg',
		ffprobe_path='/usr/local/bin/ffprobe'
    )
	info = c.probe(source)
	if info is None:
		return
	logger.debug('%s: Info: %s', basename, info.__dict__)
	
	source_format = info.format.format.split(',')[0]

	video = stream(info, 'video')
	if video is None:
		return
	logger.debug('%s: Video stream: %s', basename, video.__dict__)

	audio = stream(info, 'audio')
	if audio is None:
		return
	logger.debug('%s: Audio stream: %s', basename, audio.__dict__)

	if not check(video):
		logger.info('%s: No encoding needed', basename)
		return

	logger.info('%s: Start encoding', basename)
	conv = c.convert(
		source,
		tmpfile,
		{
			'format': source_format,
			'audio': {
				'codec': audio.codec,
				'samplerate': audio.audio_samplerate,
				'channels': audio.audio_channels
			},
			'video': {
				'codec': TARGET_CODEC,
				'width': video.video_width,
				'height': video.video_height,
				'fps': video.video_fps
			}
		}
	)
	for timecode in conv:
		logger.debug("%s: Converting %f%%", basename, timecode)

	if config.simulate:
		logger.debug("%s: Simulating, not overwriting", basename)
	else:
		logger.debug(
			"%s: Overwriting source file (%s) with encoded file (%s)",
			basename,
			basename,
			tmpfile
		)
		# Remove the source file - not necessary
		# os.remove(source)
		# Overwrite the source file
		shutil.move(tmpfile, source)

	logger.info('%s: Encoding finished', basename)


def default_log_file(dirs=None):
    if dirs is None:
        dirs = ['/var/log', '/usr/local/var/log', '/tmp']
    for d in dirs:
        if os.access(d, os.W_OK):
            return os.path.join(d, 'avconv.log')
    return os.path.expanduser('~/avconv.log')


def main():
	parser = argparse.ArgumentParser(
		description='Converting given video files, if necessary')
	parser.add_argument(
		'-s',
		'--simulate',
		action='store_true',
		default=False,
		help='simulate, don\'t overwrite source file')
	group = parser.add_argument_group('logging')
	group.add_argument(
		'--debug',
		dest='loglevel',
		action='store_const',
		const=logging.DEBUG,
		default=logging.INFO,
		help='set loglevel to debug')
	group.add_argument(
		'--info',
		dest='loglevel',
		action='store_const',
		const=logging.INFO,
		help='set loglevel to info')
	group.add_argument(
		'--warning',
		dest='loglevel',
		action='store_const',
		const=logging.WARNING,
		help='set loglevel to warning')
	group.add_argument(
		'--error',
		dest='loglevel',
		action='store_const',
		const=logging.ERROR,
		help='set loglevel to error')
	group.add_argument(
		'--critical',
		dest='loglevel',
		action='store_const',
		const=logging.CRITICAL,
		help='set loglevel to critical')
	group.add_argument(
		'-L',
		'--logfile',
		type=argparse.FileType('a'),
		default=default_log_file(),
		help='the file to log to')

	args = parser.parse_args(sys.argv[1:])

	logging.basicConfig(
		stream=args.logfile,
		level=args.loglevel,
		format="%(asctime)s %(levelname)s %(name)s: %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S")

	logger.debug('Waiting for input...')

	try:
		for line in iter(sys.stdin.readline, ''):
			try:
				process(line.strip(), args)
			except BaseException as e:
				logger.error('Error while processing: %s', e)
	except KeyboardInterrupt:
		logger.debug('Keyboard interruption')

	logger.info('Finished reading')
