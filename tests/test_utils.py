from paython.exceptions import GatewayError
from paython.lib.utils import parse_xml, is_valid_email

from nose.tools import assert_equals, raises

@raises(GatewayError)
def test_parse_xml():
    """Testing our parse xml util"""
    result = parse_xml("<lol test=\"woot\">waaa<inside>heh</inside></lol>")
    expected = {'lol': {'attribute': {'test': 'woot'},
                      'meta': {'#text': 'waaa', 'inside': 'heh'}}}

    assert_equals(result, expected)

    parse_xml("<lol>testing invalid xml<lol>")


def test_cdata_parse_xml():
    """testing when we pass cdata to the xml"""
    result = parse_xml("<lol><inside><![CDATA[???]]></inside></lol>")
    expected = {'lol': {'inside': '???'}}

    assert_equals(result, expected)

def test_multiple_child_nodes():
    """testing multiple child nodes"""
    result = parse_xml("<lol><first>text 1</first><second>text 2</second></lol>")
    expected = {'lol': {'first': 'text 1', 'second': 'text 2'}}

    assert_equals(result, expected)

def test_append_to_root():
    """testing append to root entity"""
    result = parse_xml("<lol><first>text 1</first><first>text 2</first></lol>")
    expected = {'lol': {'first': ['text 1', 'text 2']}}

    assert_equals(result, expected)

def test_valid_email():
    """testing our email validation"""
    assert_equals(is_valid_email("lol@lol.com") is None, False)
