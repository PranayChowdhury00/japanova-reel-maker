"""V4.7 timeline export graph regression tests.

Run from repository root: python -m unittest discover -s tests -v
Does not invoke FFmpeg or external AI services.
"""
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import server


class TimelineTests(unittest.TestCase):
    def settings(self):
        return {
            'quality': 'lite', 'count': 2, 'durations': [4.0, 5.0],
            'transitions': ['fade', 'fade'],
            'subtitle_mode': 'scene', 'subtitles': True,
            'caption_visible': [True, False],
            'caption_delays': [1.2, 0.0],
            'avatar_visible': [True, False],
            'avatar': 'boy', 'avatar_position': 'center',
            'motion_style': 'fade', 'motion_position': 'right',
            'motion_size': 100, 'motion_items': [],
        }

    def test_caption_delay_and_presenter_visibility(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = pathlib.Path(temp)
            for name in ('base.png', 'scene0.png', 'scene1.png',
                         'subtitle0.png', 'subtitle1.png',
                         'avatar-closed.png', 'avatar-open.png', 'avatar-blink.png'):
                (folder / name).write_bytes(b'x')
            with patch.object(server.shutil, 'which', return_value='ffmpeg'), \
                 patch.object(server, 'mouth_intervals', return_value=[]):
                cmd = server.make_command(folder, self.settings(), False, False)
            graph = cmd[cmd.index('-filter_complex') + 1]
            self.assertIn('caption0', graph)
            self.assertIn('caption1', graph)
            self.assertIn('enable=0[caption1]', graph)
            self.assertIn('1.20000', graph)
            self.assertIn('between(t\\,0.00000\\,4.00000)', graph)
            self.assertIn('avatar0', graph)

    def test_invalid_caption_delay_rejected(self):
        settings = self.settings()
        settings['caption_delays'] = [5.0, 0.0]
        with patch.object(server.shutil, 'which', return_value='ffmpeg'):
            with self.assertRaisesRegex(ValueError, 'Caption delay'):
                server.make_command(pathlib.Path('.'), settings, False, False)

    def test_legacy_projects_default_visible(self):
        settings = self.settings()
        settings.pop('caption_delays')
        settings.pop('caption_visible')
        settings.pop('avatar_visible')
        with tempfile.TemporaryDirectory() as temp:
            folder = pathlib.Path(temp)
            for name in ('subtitle0.png','subtitle1.png',
                         'avatar-closed.png','avatar-open.png','avatar-blink.png'):
                (folder / name).write_bytes(b'x')
            with patch.object(server.shutil, 'which', return_value='ffmpeg'), \
                 patch.object(server, 'mouth_intervals', return_value=[]):
                cmd = server.make_command(folder, settings, False, False)
            self.assertIn('-filter_complex', cmd)


if __name__ == '__main__':
    unittest.main()
