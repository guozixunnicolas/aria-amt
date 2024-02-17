import unittest
import logging
import os

from amt.tokenizer import AmtTokenizer
from aria.data.midi import MidiDict

logging.basicConfig(level=logging.INFO)
if os.path.isdir("tests/test_results") is False:
    os.mkdir("tests/test_results")


class TestAmtTokenizer(unittest.TestCase):
    def test_tokenize(self):
        def _tokenize_detokenize(mid_name: str):
            START = 5000
            END = 10000

            tokenizer = AmtTokenizer()
            midi_dict = MidiDict.from_midi(f"tests/test_data/{mid_name}")
            tokenized_seq = tokenizer._tokenize_midi_dict(
                midi_dict=midi_dict,
                start_ms=START,
                end_ms=END,
            )
            logging.info(f"{mid_name} tokenized:")
            logging.info(tokenized_seq)

            _midi_dict = tokenizer._detokenize_midi_dict(
                tokenized_seq, END - START
            )
            _mid = _midi_dict.to_midi()
            _mid.save(f"tests/test_results/{mid_name}")
            logging.info(f"{mid_name} note_msgs:")
            for msg in _midi_dict.note_msgs:
                logging.info(msg)

        _tokenize_detokenize(mid_name="basic.mid")
        _tokenize_detokenize(mid_name="147.mid")
        _tokenize_detokenize(mid_name="beethoven_moonlight.mid")

    def test_aug(self):
        def aug(_midi_dict: MidiDict, _start_ms: int, _end_ms: int):
            _tokenized_seq = tokenizer._tokenize_midi_dict(
                midi_dict=_midi_dict,
                start_ms=_start_ms,
                end_ms=_end_ms,
            )

            aug_fn = tokenizer.export_msg_mixup()
            _aug_tokenized_seq = aug_fn(_tokenized_seq)
            self.assertEqual(len(_tokenized_seq), len(_aug_tokenized_seq))

            return _tokenized_seq, _aug_tokenized_seq

        DELTA_MS = 5000
        tokenizer = AmtTokenizer()
        midi_dict = MidiDict.from_midi("tests/test_data/bach.mid")
        __end_ms = midi_dict.note_msgs[-1]["data"]["end"]

        for idx, __start_ms in enumerate(range(0, __end_ms, DELTA_MS)):
            tokenized_seq, aug_tokenized_seq = aug(
                midi_dict, __start_ms, __start_ms + DELTA_MS
            )

            self.assertEqual(
                len(
                    tokenizer._detokenize_midi_dict(
                        tokenized_seq, DELTA_MS
                    ).note_msgs
                ),
                len(
                    tokenizer._detokenize_midi_dict(
                        aug_tokenized_seq, DELTA_MS
                    ).note_msgs
                ),
            )

            if idx == 0:
                logging.info(
                    f"msg mixup: {tokenized_seq} ->\n{aug_tokenized_seq}"
                )

                _midi_dict = tokenizer._detokenize_midi_dict(
                    tokenized_seq, DELTA_MS
                )
                _mid = _midi_dict.to_midi()
                _mid.save(f"tests/test_results/bach_orig.mid")

                _midi_dict = tokenizer._detokenize_midi_dict(
                    aug_tokenized_seq, DELTA_MS
                )
                _mid = _midi_dict.to_midi()
                _mid.save(f"tests/test_results/bach_aug.mid")


if __name__ == "__main__":
    unittest.main()
