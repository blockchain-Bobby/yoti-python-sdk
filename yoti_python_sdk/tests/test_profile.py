# -*- coding: utf-8 -*-
import collections
import json
import logging

import pytest

from yoti_python_sdk import config
from yoti_python_sdk.attribute import Attribute
from yoti_python_sdk.profile import Profile
from yoti_python_sdk.protobuf.protobuf import Protobuf
from yoti_python_sdk.tests import attribute_fixture_parser, image_helper
from yoti_python_sdk.tests.protobuf_attribute import ProtobufAttribute

ADDRESS_FORMAT_KEY = "address_format"
ADDRESS_FORMAT_VALUE = 1
INDIA_FORMAT_VALUE = 2
USA_FORMAT_VALUE = 3

BUILDING_NUMBER_KEY = "building_number"
BUILDING_NUMBER_VALUE = "15a"

CARE_OF_KEY = "care_of"
CARE_OF_VALUE = "S/O: Name"

STATE_KEY = "state"
INDIA_STATE_VALUE = "Punjab"
USA_STATE_VALUE = "AL"

BUILDING_KEY = "building"
BUILDING_VALUE = "House No.1111-A"

STREET_KEY = "street"
STREET_VALUE = "42nd Street"

DISTRICT_KEY = "district"
DISTRICT_VALUE = "DISTRICT 10"

SUBDISTRICT_KEY = "subdistrict"
SUBDISTRICT_VALUE = "Sub-DISTRICT 10"

POST_OFFICE_KEY = "post_office"
INDIA_POST_OFFICE_VALUE = "Rajguru Nagar"

ADDRESS_LINE_1_KEY = "address_line_1"
ADDRESS_LINE_1_VALUE = "15a North Street"

TOWN_CITY_KEY = "town_city"
TOWN_CITY_VALUE = "TOWN/CITY NAME"

POSTAL_CODE_KEY = "postal_code"
POSTAL_CODE_VALUE = "SM5 2HW"
INDIA_POSTAL_CODE_VALUE = "141012"
USA_POSTAL_CODE_VALUE = "36201"

COUNTRY_ISO_KEY = "country_iso"
COUNTRY_ISO_VALUE = "GBR"
INDIA_COUNTRY_ISO_VALUE = "IND"
USA_COUNTRY_ISO_VALUE = "USA"

COUNTRY_KEY = "country"
COUNTRY_VALUE = "UK"
INDIA_COUNTRY_VALUE = "India"
USA_COUNTRY_VALUE = "USA"

FORMATTED_ADDRESS_VALUE = "15a North Street\nCARSHALTON\nSM5 2HW\nUK"
INDIA_FORMATTED_ADDRESS_VALUE = 'S/O: Name\nHouse No.1111-A\n42nd Street\nTOWN/CITY NAME\nSub-DISTRICT 10\nDISTRICT 10\nPunjab\n141012\nRajgura Nagar\nIndia'
USA_FORMATTED_ADDRESS_VALUE = "15a North Street\nTOWN/CITY NAME\nAL\n36201\nUSA"


def create_single_attribute_list(name, value, anchors, content_type):
    attribute = ProtobufAttribute(name, value, anchors, content_type)

    attribute_list = list()
    attribute_list.append(attribute)
    return attribute_list


def create_attribute_list_with_selfie_field():
    return create_single_attribute_list(
        name=config.ATTRIBUTE_SELFIE,
        value="base64(ง •̀_•́)ง",
        anchors=None,
        content_type=Protobuf.CT_JPEG)


def create_attribute_list_with_email_field():
    return create_single_attribute_list(
        name=config.ATTRIBUTE_EMAIL_ADDRESS,
        value="y@ti.com".encode(),
        anchors=None,
        content_type=Protobuf.CT_STRING)


def create_attribute_list_with_structured_postal_address_field(json_address_value):
    return create_single_attribute_list(
        name=config.ATTRIBUTE_STRUCTURED_POSTAL_ADDRESS,
        value=json_address_value,
        anchors=None,
        content_type=Protobuf.CT_JSON)


@pytest.mark.parametrize(
    "string, expected_int", [("0", 0), ("1", 1), ("123", 123), ("-10", -10), ("-1", -1)]
)
def test_try_parse_int_value(string, expected_int):
    attribute_name = "int_attribute"
    attribute_list = create_single_attribute_list(
        name=attribute_name,
        value=str.encode(string),
        anchors=None,
        content_type=Protobuf.CT_INT)

    profile = Profile(attribute_list)
    int_attribute = profile.get_attribute(attribute_name)
    assert int_attribute.value == expected_int


def test_error_parsing_attribute_has_none_value():
    int_attribute_name = "int_attribute"

    attribute_list = create_single_attribute_list(
        name=int_attribute_name,
        value=str.encode("invalid_int"),
        anchors=None,
        content_type=Protobuf.CT_INT)

    # disable logging for the below call: warning shown as int is invalid
    logger = logging.getLogger()
    logger.propagate = False

    profile = Profile(attribute_list)

    logger.propagate = True

    assert profile.get_attribute(int_attribute_name) is None


@pytest.mark.parametrize("content_type", [Protobuf.CT_DATE, Protobuf.CT_INT, Protobuf.CT_JPEG, Protobuf.CT_PNG, Protobuf.CT_JSON, Protobuf.CT_UNDEFINED])
def test_parse_empty_values_returns_none(content_type):
    attribute_name = "attribute_name"

    attribute_list = create_single_attribute_list(
        name=attribute_name,
        value=b'',
        anchors=None,
        content_type=content_type)

    # disable logging for the below call: warning logged as value is empty
    logger = logging.getLogger()
    logger.propagate = False

    profile = Profile(attribute_list)

    logger.propagate = True

    assert profile.get_attribute(attribute_name) is None


@pytest.mark.parametrize("value", [b'', "".encode()])
def test_parse_empty_string_value_returns_attribute(value):
    attribute_name = "attribute_name"

    attribute_list = create_single_attribute_list(
        name=attribute_name,
        value=value,
        anchors=None,
        content_type=Protobuf.CT_STRING)

    profile = Profile(attribute_list)

    assert profile.get_attribute(attribute_name).value == ""


def test_error_parsing_attribute_does_not_affect_other_attribute():
    string_attribute_name = "string_attribute"
    int_attribute_name = "int_attribute"
    string_value = "string"

    attribute_list = list()

    attribute_list.append(ProtobufAttribute(
        name=string_attribute_name,
        value=str.encode(string_value),
        anchors=None,
        content_type=Protobuf.CT_STRING))

    attribute_list.append(ProtobufAttribute(
        name=int_attribute_name,
        value=str.encode("invalid_int"),
        anchors=None,
        content_type=Protobuf.CT_INT))

    # disable logging for the below call: warning shown as int is invalid
    logger = logging.getLogger()
    logger.propagate = False

    profile = Profile(attribute_list)

    logger.propagate = True

    assert len(profile.attributes) == 1

    retrieved_string_attribute = profile.get_attribute(string_attribute_name)
    assert retrieved_string_attribute.name == string_attribute_name
    assert retrieved_string_attribute.value == string_value


def test_try_parse_structured_postal_address_uk():
    structured_postal_address = {ADDRESS_FORMAT_KEY: ADDRESS_FORMAT_VALUE,
                                 BUILDING_NUMBER_KEY: BUILDING_NUMBER_VALUE,
                                 ADDRESS_LINE_1_KEY: ADDRESS_LINE_1_VALUE,
                                 TOWN_CITY_KEY: TOWN_CITY_VALUE,
                                 POSTAL_CODE_KEY: POSTAL_CODE_VALUE,
                                 COUNTRY_ISO_KEY: COUNTRY_ISO_VALUE,
                                 COUNTRY_KEY: COUNTRY_VALUE,
                                 config.KEY_FORMATTED_ADDRESS: FORMATTED_ADDRESS_VALUE}

    structured_postal_address_json = json.dumps(structured_postal_address).encode()

    profile = Profile(create_attribute_list_with_structured_postal_address_field(structured_postal_address_json))

    actual_structured_postal_address_profile = profile.structured_postal_address.value

    assert type(actual_structured_postal_address_profile) is collections.OrderedDict
    assert actual_structured_postal_address_profile[ADDRESS_FORMAT_KEY] == ADDRESS_FORMAT_VALUE
    assert actual_structured_postal_address_profile[BUILDING_NUMBER_KEY] == BUILDING_NUMBER_VALUE
    assert actual_structured_postal_address_profile[ADDRESS_LINE_1_KEY] == ADDRESS_LINE_1_VALUE
    assert actual_structured_postal_address_profile[TOWN_CITY_KEY] == TOWN_CITY_VALUE
    assert actual_structured_postal_address_profile[POSTAL_CODE_KEY] == POSTAL_CODE_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_ISO_KEY] == COUNTRY_ISO_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_KEY] == COUNTRY_VALUE
    assert actual_structured_postal_address_profile[config.KEY_FORMATTED_ADDRESS] == FORMATTED_ADDRESS_VALUE


def test_other_json_type_is_parsed():
    json_attribute_name = "other_json"
    key_a = "keyA"
    key_b = "keyB"
    value_a = "valueA"
    value_b = "valueB"
    json_value = {key_a: value_a,
                  key_b: value_b}

    encoded_json = json.dumps(json_value).encode()

    attribute_list = create_single_attribute_list(
        name=json_attribute_name,
        value=encoded_json,
        anchors=None,
        content_type=Protobuf.CT_JSON)

    profile = Profile(attribute_list)

    retrieved_attribute = profile.get_attribute(json_attribute_name)

    assert retrieved_attribute.name == json_attribute_name
    assert type(retrieved_attribute.value) is collections.OrderedDict
    assert retrieved_attribute.value[key_a] == value_a
    assert retrieved_attribute.value[key_b] == value_b


def test_try_parse_structured_postal_address_india():
    structured_postal_address = {ADDRESS_FORMAT_KEY: INDIA_FORMAT_VALUE,
                                 CARE_OF_KEY: CARE_OF_VALUE,
                                 BUILDING_KEY: BUILDING_VALUE,
                                 STREET_KEY: STREET_VALUE,
                                 TOWN_CITY_KEY: TOWN_CITY_VALUE,
                                 SUBDISTRICT_KEY: SUBDISTRICT_VALUE,
                                 DISTRICT_KEY: DISTRICT_VALUE,
                                 STATE_KEY: INDIA_STATE_VALUE,
                                 POSTAL_CODE_KEY: INDIA_POSTAL_CODE_VALUE,
                                 POST_OFFICE_KEY: INDIA_POST_OFFICE_VALUE,
                                 COUNTRY_ISO_KEY: INDIA_COUNTRY_ISO_VALUE,
                                 COUNTRY_KEY: INDIA_COUNTRY_VALUE,
                                 config.KEY_FORMATTED_ADDRESS: INDIA_FORMATTED_ADDRESS_VALUE}

    structured_postal_address_bytes = json.dumps(structured_postal_address).encode()

    profile = Profile(create_attribute_list_with_structured_postal_address_field(structured_postal_address_bytes))

    actual_structured_postal_address_profile = profile.structured_postal_address.value

    assert type(actual_structured_postal_address_profile) is collections.OrderedDict
    assert actual_structured_postal_address_profile[ADDRESS_FORMAT_KEY] == INDIA_FORMAT_VALUE
    assert actual_structured_postal_address_profile[CARE_OF_KEY] == CARE_OF_VALUE
    assert actual_structured_postal_address_profile[BUILDING_KEY] == BUILDING_VALUE
    assert actual_structured_postal_address_profile[STREET_KEY] == STREET_VALUE
    assert actual_structured_postal_address_profile[TOWN_CITY_KEY] == TOWN_CITY_VALUE
    assert actual_structured_postal_address_profile[SUBDISTRICT_KEY] == SUBDISTRICT_VALUE
    assert actual_structured_postal_address_profile[DISTRICT_KEY] == DISTRICT_VALUE
    assert actual_structured_postal_address_profile[STATE_KEY] == INDIA_STATE_VALUE
    assert actual_structured_postal_address_profile[POSTAL_CODE_KEY] == INDIA_POSTAL_CODE_VALUE
    assert actual_structured_postal_address_profile[POST_OFFICE_KEY] == INDIA_POST_OFFICE_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_ISO_KEY] == INDIA_COUNTRY_ISO_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_KEY] == INDIA_COUNTRY_VALUE
    assert actual_structured_postal_address_profile[config.KEY_FORMATTED_ADDRESS] == INDIA_FORMATTED_ADDRESS_VALUE


def test_try_parse_structured_postal_address_usa():
    structured_postal_address = {ADDRESS_FORMAT_KEY: USA_FORMAT_VALUE,
                                 ADDRESS_LINE_1_KEY: ADDRESS_LINE_1_VALUE,
                                 TOWN_CITY_KEY: TOWN_CITY_VALUE,
                                 STATE_KEY: USA_STATE_VALUE,
                                 POSTAL_CODE_KEY: USA_POSTAL_CODE_VALUE,
                                 COUNTRY_ISO_KEY: USA_COUNTRY_ISO_VALUE,
                                 COUNTRY_KEY: USA_COUNTRY_VALUE,
                                 config.KEY_FORMATTED_ADDRESS: USA_FORMATTED_ADDRESS_VALUE}

    structured_postal_address_bytes = json.dumps(structured_postal_address).encode()

    profile = Profile(create_attribute_list_with_structured_postal_address_field(structured_postal_address_bytes))

    actual_structured_postal_address_profile = profile.structured_postal_address.value

    assert type(actual_structured_postal_address_profile) is collections.OrderedDict
    assert actual_structured_postal_address_profile[ADDRESS_FORMAT_KEY] == USA_FORMAT_VALUE
    assert actual_structured_postal_address_profile[ADDRESS_LINE_1_KEY] == ADDRESS_LINE_1_VALUE
    assert actual_structured_postal_address_profile[TOWN_CITY_KEY] == TOWN_CITY_VALUE
    assert actual_structured_postal_address_profile[STATE_KEY] == USA_STATE_VALUE
    assert actual_structured_postal_address_profile[POSTAL_CODE_KEY] == USA_POSTAL_CODE_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_ISO_KEY] == USA_COUNTRY_ISO_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_KEY] == USA_COUNTRY_VALUE
    assert actual_structured_postal_address_profile[config.KEY_FORMATTED_ADDRESS] == USA_FORMATTED_ADDRESS_VALUE


def test_try_parse_structured_postal_address_nested_json():
    formatted_address_json = {
        "item1": [
            [1, 'a1'],
            [2, 'a2'],
        ],
        "item2": [
            [3, 'b3'],
            [4, 'b4'],
        ],
    }

    structured_postal_address = {ADDRESS_FORMAT_KEY: ADDRESS_FORMAT_VALUE,
                                 BUILDING_NUMBER_KEY: BUILDING_NUMBER_VALUE,
                                 ADDRESS_LINE_1_KEY: ADDRESS_LINE_1_VALUE,
                                 TOWN_CITY_KEY: TOWN_CITY_VALUE,
                                 POSTAL_CODE_KEY: POSTAL_CODE_VALUE,
                                 COUNTRY_ISO_KEY: COUNTRY_ISO_VALUE,
                                 COUNTRY_KEY: COUNTRY_VALUE,
                                 config.KEY_FORMATTED_ADDRESS: formatted_address_json}

    structured_postal_address_bytes = json.dumps(structured_postal_address).encode()

    profile = Profile(create_attribute_list_with_structured_postal_address_field(structured_postal_address_bytes))

    actual_structured_postal_address_profile = profile.structured_postal_address.value

    assert type(actual_structured_postal_address_profile) is collections.OrderedDict
    assert actual_structured_postal_address_profile[ADDRESS_FORMAT_KEY] == ADDRESS_FORMAT_VALUE
    assert actual_structured_postal_address_profile[BUILDING_NUMBER_KEY] == BUILDING_NUMBER_VALUE
    assert actual_structured_postal_address_profile[ADDRESS_LINE_1_KEY] == ADDRESS_LINE_1_VALUE
    assert actual_structured_postal_address_profile[TOWN_CITY_KEY] == TOWN_CITY_VALUE
    assert actual_structured_postal_address_profile[POSTAL_CODE_KEY] == POSTAL_CODE_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_ISO_KEY] == COUNTRY_ISO_VALUE
    assert actual_structured_postal_address_profile[COUNTRY_KEY] == COUNTRY_VALUE

    assert actual_structured_postal_address_profile[config.KEY_FORMATTED_ADDRESS] == formatted_address_json


def test_set_address_to_be_formatted_address():
    structured_postal_address = {config.KEY_FORMATTED_ADDRESS: FORMATTED_ADDRESS_VALUE}
    structured_postal_address_bytes = json.dumps(structured_postal_address).encode()

    profile = Profile(create_attribute_list_with_structured_postal_address_field(structured_postal_address_bytes))

    assert profile.postal_address.value == FORMATTED_ADDRESS_VALUE


def test_document_images():
    document_images_attribute = attribute_fixture_parser.get_attribute_from_base64_text(
        attribute_fixture_parser.ATTRIBUTE_DOCUMENT_IMAGES)

    attribute_list = list()
    attribute_list.append(document_images_attribute)

    profile = Profile(attribute_list)

    document_images_attribute = profile.document_images
    assert len(document_images_attribute.value) == 2
    image_helper.assert_is_expected_image(document_images_attribute.value[0], "jpeg", "vWgD//2Q==")
    image_helper.assert_is_expected_image(document_images_attribute.value[1], "jpeg", "38TVEH/9k=")


def test_nested_multi_value():
    attribute_name = "nested_multi_value"
    inner_multi_value = attribute_fixture_parser.parse_multi_value()

    outer_tuple = (inner_multi_value,)

    profile = Profile(profile_attributes=None)
    profile.attributes[attribute_name] = Attribute(
        name=attribute_name,
        value=outer_tuple,
        anchors=None)

    retrieved_multi_value = profile.get_attribute(attribute_name)

    assert isinstance(retrieved_multi_value.value, tuple)

    for item in retrieved_multi_value.value:
        assert isinstance(item, tuple)

    image_helper.assert_is_expected_image(retrieved_multi_value.value[0][0], "jpeg", "vWgD//2Q==")
    image_helper.assert_is_expected_image(retrieved_multi_value.value[0][1], "jpeg", "38TVEH/9k=")


def test_get_attribute_document_images():
    attribute_list = create_single_attribute_list(
        name=config.ATTRIBUTE_DOCUMENT_IMAGES,
        value=b'',
        anchors=None,
        content_type=Protobuf.CT_MULTI_VALUE)

    profile = Profile(attribute_list)

    assert profile.get_attribute(config.ATTRIBUTE_DOCUMENT_IMAGES) == profile.document_images


def test_get_attribute_selfie():
    profile = Profile(create_attribute_list_with_selfie_field())

    assert profile.get_attribute(config.ATTRIBUTE_SELFIE) == profile.selfie


def test_get_attribute_email_address():
    profile = Profile(create_attribute_list_with_email_field())

    assert profile.get_attribute(config.ATTRIBUTE_EMAIL_ADDRESS) == profile.email_address


def test_get_attribute_returns_none():
    profile = Profile(None)

    assert profile.get_attribute(config.ATTRIBUTE_SELFIE) is None
