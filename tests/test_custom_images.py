"""Custom image export and portable project validation.

Run: python -m unittest discover -s tests -v
Uses mocked FFmpeg discovery; does not encode a video.
"""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import server


class CustomImageTests(unittest.TestCase):
    def settings(self):
        return {
            'quality': 'lite', 'count': 2, 'durations': [4.0, 5.0],
            'transitions': ['fade', 'fade'], 'subtitle_mode': 'off',
            'avatar': 'off', 'motion_style': 'fade', 'motion_position': 'right',
            'motion_size': 100, 'custom_images': [
                {'scene': 0, 'start': 0.8, 'duration': 2.0},
                {'scene': 1, 'start': 4.1, 'duration': 1.8},
            ],
        }

    def test_custom_layers_added_before_audio_and_overlaid(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)
            for name in ('base.png','scene0.png','scene1.png','custom0.png','custom1.png'):
                (p/name).write_bytes(b'fake-png')
            with patch.object(server.shutil, 'which', return_value='ffmpeg'):
                command=server.make_command(p,self.settings(),False,False)
            self.assertIn('custom0.png', ' '.join(command))
            self.assertIn('custom1.png', ' '.join(command))
            graph=command[command.index('-filter_complex')+1]
            self.assertIn('customout0',graph)
            self.assertIn('customout1',graph)
            self.assertIn('0.80000',graph)
            self.assertIn('4.10000',graph)

    def test_rejects_timing_outside_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings=self.settings()
            settings['custom_images'][0]['start']=3.5
            with patch.object(server.shutil, 'which', return_value='ffmpeg'):
                with self.assertRaisesRegex(ValueError,'Custom image timing'):
                    server.make_command(pathlib.Path(tmp),settings,False,False)

    def test_portable_project_accepts_embedded_image(self):
        data = {
            'format':'japanova-reel-project','version':1,'script':'Hello.',
            'settings':{},'scenes':[{'text':'Hello.'}],
            'durations':[4.0],
            'image_library':[{'id':'abc123','name':'Logo.png',
                'data':'data:image/png;base64,iVBORw0KGgo='}],
        }
        restored=server.project_json(json.dumps(data).encode('utf8'))
        self.assertEqual(restored['image_library'][0]['id'],'abc123')

    def test_rejects_bad_asset_mime(self):
        data = {
            'format':'japanova-reel-project','version':1,'script':'Hello.',
            'settings':{},'scenes':[{'text':'Hello.'}],
            'durations':[4.0],
            'image_library':[{'id':'abc123','name':'x.svg',
                'data':'data:image/svg+xml;base64,AAAA'}],
        }
        with self.assertRaisesRegex(ValueError,'Invalid image type'):
            server.project_json(json.dumps(data).encode('utf8'))


if __name__=='__main__':
    unittest.main()
