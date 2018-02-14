import traceback
import pytest


def assert_exit_code(cli_run_result, expected_code):
    if expected_code != cli_run_result.exit_code:
        pytest.fail(
            "Got unexpected exit code: %s, expects: %s.\n\n[CLI output]\n%s\n[Trace]\n%s" % (
                cli_run_result.exit_code,
                expected_code,
                cli_run_result.output,
                ''.join(traceback.format_exception(*cli_run_result.exc_info))
            )
        )
