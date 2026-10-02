from biliclass_m0.probes.translation import decode_candidate


def test_argos_separator_cleanup_preserves_code_underscores():
    class Tokenizer:
        def decode(self, _pieces):
            return "Group▁discussion with variable_name"

    assert decode_candidate(Tokenizer(), []) == "Group discussion with variable_name"
