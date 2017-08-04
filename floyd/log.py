import logging
import sys

logger = logging.getLogger('floyd')


def configure_logger(verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format='%(message)s',
                        level=log_level,
                        stream=sys.stdout)
