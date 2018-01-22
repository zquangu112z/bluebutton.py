###############################################################################
# Copyright 2015 University of Florida. All rights reserved.
# This file is part of the BlueButton.py project.
# Use of this source code is governed by the license found in the LICENSE file.
###############################################################################

import datetime
from ..core import wrappers
from . import ccda
from . import c32
import logging

unstructerdValueTypes = ["ST", "ED"]


def detect(data):
    if not hasattr(data, 'template'):
        return 'json'

    if not data.template('2.16.840.1.113883.3.88.11.32.1').is_empty():
        return 'c32'

    if not data.template('2.16.840.1.113883.10.20.22.1.1').is_empty():
        return 'ccda'
    logging.warning("type: unknown")

    return 'unknown'


def entries(element):
    """
    Get entries within an element (with tag name 'entry'), adds an `each` method
    """
    els = element.els_by_tag('entry')
    els.each = lambda callback: map(callback, els)
    return els


def parse_address(address_element):
    """
    Parses an HL7 address (streetAddressLine [], city, state, postalCode,
    country)

    :param address_element:
    :return:
    """
    els = address_element.els_by_tag('streetAddressLine')
    street = [e.val() for e in els if e.val()]

    city = address_element.tag('city').val()
    state = address_element.tag('state').val()
    zip = address_element.tag('postalCode').val()
    country = address_element.tag('country').val()

    return wrappers.ObjectWrapper(
        street=street,
        city=city,
        state=state,
        zip=zip,
        country=country,
    )


def parse_date(string):
    """
    Parses an HL7 date in String form and creates a new Date object.

    TODO: CCDA dates can be in form:
        <effectiveTime value="20130703094812"/>
    ...or:
        <effectiveTime>
            <low value="19630617120000"/>
            <high value="20110207100000"/>
        </effectiveTime>

    For the latter, parse_date will not be given type `string` and will return
    `None`.

    The syntax is "YYYYMMDDHHMMSS.UUUU[+|-ZZzz]" where digits can be omitted
    the right side to express less precision
    """
    try:
        if not isinstance(string, str):
            return None

        # ex. value="1999" translates to 1 Jan 1999
        if len(string) == 4:
            return datetime.date(int(string), 1, 1)

        year = int(string[0:4])
        month = int(string[4:6])
        day = int(string[6:8] or 1)

        # check for time info (the presence of at least hours and mins after the
        # date)
        if len(string) >= 12:
            hour = int(string[8:10])
            mins = int(string[10:12])
            secs = string[12:14]
            secs = int(secs) if secs else 0

            # check for timezone info (the presence of chars after the seconds
            # place)
            timezone = wrappers.FixedOffset.from_string(string[14:])
            return datetime.datetime(year, month, day, hour, mins, secs,
                                     tzinfo=timezone)

        return datetime.date(year, month, day)
    except ValueError as e:
        # In case we cannot parse the effectiveTime, return the string
        logging.warning("Cannnot parse %r to datetime", string)
        return string


def parse_name(name_element):
    prefix = name_element.tag('prefix').val()
    els = name_element.els_by_tag('given')
    given = [e.val() for e in els if e.val()]
    family = name_element.tag('family').val()

    return wrappers.ObjectWrapper(
        prefix=prefix,
        given=given,
        family=family
    )


def extractUnit(string):
    words = str.split(string, " ")
    if len(words) > 1 and is_number(words[0]) and not is_number(words[1]):
        return words[0], words[1]
    else:
        return string, None


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
