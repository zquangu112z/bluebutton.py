###############################################################################
# Copyright 2015 University of Florida. All rights reserved.
# This file is part of the BlueButton.py project.
# Use of this source code is governed by the license found in the LICENSE file.
###############################################################################

from . import core
from . import documents
from . import parsers

from fii.cfg import getConfig
from fii.log import getLogger

config = getConfig(__name__)
logger = getLogger(__name__)


__version__ = '0.5.1'


class BlueButton(object):
    def __init__(self, source, options=None):
        cdaType, parsed_document, parsed_data = None, None, None

        if options is None:
            opts = dict()

        # parsed_data is an instance of core/xml.py/_Element
        parsed_data = core.parse_data(source)

        if 'parser' in opts:
            parsed_document = opts['parser']()
        else:
            cdaType = documents.detect(parsed_data)
            if 'c32' == cdaType:
                logger.info("c32")
                parsed_data = documents.c32.process(parsed_data)
                # @TODO: add specific parser for C32
                parsed_document = parsers.ccda.run(parsed_data)
            elif 'ccda' == cdaType:
                logger.info("ccda")
                parsed_data = documents.ccda.process(parsed_data)
                parsed_document = parsers.ccda.run(parsed_data)
            elif 'json' == cdaType:
                logger.info("json")
                # @TODO: add support for JSON
                pass
            else:
                logger.warning(cdaType)

        self.type = cdaType
        self.data = parsed_document
        self.source = parsed_data
