"""Regression tests for the Auto Duration 60-second cap.

Run: python -m unittest discover -s tests -v
No internet, FFmpeg or TTS calls are required.
"""
import unittest
from unittest.mock import patch
from pathlib import Path
import voice_engine


class DurationTests(unittest.TestCase):
    def generate(self, lengths, mode='auto'):
        async def fake_edge(scenes, voice, speed, folder):
            return [folder / ('fake%d.mp3' % i) for i in range(len(scenes))], [[] for _ in scenes]

        class FakeOutput:
            def read_bytes(self):
                return b'fake audio bytes'

        with patch.object(voice_engine, 'edge_generate', side_effect=fake_edge), \
             patch.object(voice_engine, 'probe_seconds', side_effect=lengths), \
             patch.object(voice_engine, '_sync_audio', return_value=FakeOutput()), \
             patch.object(voice_engine.shutil, 'which', return_value='ffmpeg'):
            return voice_engine.make_voice(
                ['একটি সাধারণ বাংলা বাক্য।' for _ in lengths],
                'bn-BD-PradeepNeural', 1.0, duration_mode=mode)

    def test_46_second_script_is_not_rejected_or_cut(self):
        result = self.generate([21.0, 25.1])
        self.assertGreater(result['total_seconds'], 46.1)
        self.assertLess(result['total_seconds'], 60.0)
        self.assertAlmostEqual(sum(result['durations']), result['total_seconds'], places=2)

    def test_short_script_remains_short(self):
        result = self.generate([7.5])
        self.assertLess(result['total_seconds'], 10)

    def test_fixed_30_still_rejects_long_speech(self):
        with self.assertRaisesRegex(ValueError, 'Fixed 30 Seconds'):
            self.generate([21.0, 25.1], 'fixed30')

    def test_auto_exceeding_60_is_clearly_rejected(self):
        with self.assertRaisesRegex(ValueError, '60s limit'):
            self.generate([30.0, 31.0])


if __name__ == '__main__':
    unittest.main()
