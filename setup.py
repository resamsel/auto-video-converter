#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
	name="auto-video-converter",
	version='0.0.1',
	author="René Samselnig",
	author_email="me@resamsel.com",
	description="Automatic video encoding",
	keywords="video encoding",

	entry_points={
		'console_scripts': [
			'avconv = avconv:main'
		]
	}
)
