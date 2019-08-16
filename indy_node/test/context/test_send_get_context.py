import json

import pytest

from indy_common.constants import GET_CONTEXT, CONTEXT_TYPE, RS_TYPE, CONTEXT_NAME, CONTEXT_VERSION
from indy_node.test.context.helper import W3C_BASE_CONTEXT
from plenum.common.exceptions import RequestNackedException

from plenum.common.constants import DATA, NAME, VERSION, TXN_METADATA, TXN_METADATA_SEQ_NO

from plenum.common.types import OPERATION

from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies

from indy_node.test.api.helper import sdk_write_context
from indy_node.test.helper import createUuidIdentifier, modify_field


TEST_CONTEXT_NAME = "Base_Context"
TEST_CONTEXT_VERSION = "1.0"


@pytest.fixture(scope="module")
def send_context(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    context_json, _ = sdk_write_context(looper, sdk_pool_handle, sdk_wallet_trustee,
                                        W3C_BASE_CONTEXT,
                                        TEST_CONTEXT_NAME,
                                        TEST_CONTEXT_VERSION)
    return json.loads(context_json)['id']


@pytest.fixture(scope="module")
def send_context_seq_no(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, reply = sdk_write_context(looper, sdk_pool_handle, sdk_wallet_trustee)
    return reply['result'][TXN_METADATA][TXN_METADATA_SEQ_NO]


@pytest.fixture(scope="module")
def send_context_req(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    context_json, reply = sdk_write_context(
        looper, sdk_pool_handle,
        sdk_wallet_trustee,
        W3C_BASE_CONTEXT,
        TEST_CONTEXT_NAME,
        TEST_CONTEXT_VERSION)
    return context_json, reply


def test_send_get_context_succeeds(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': TEST_CONTEXT_NAME,
                'version': TEST_CONTEXT_VERSION,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                     get_context_txn_json)])
    assert rep[0][1]['result']['seqNo']
    assert rep[0][1]['result']['data']['meta'][RS_TYPE] == CONTEXT_TYPE
    assert rep[0][1]['result']['data']['meta'][CONTEXT_NAME] == TEST_CONTEXT_NAME
    assert rep[0][1]['result']['data']['meta'][CONTEXT_VERSION] == TEST_CONTEXT_VERSION
    assert rep[0][1]['result']['data']['data'] == W3C_BASE_CONTEXT


def test_send_get_context_as_client(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_client, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': TEST_CONTEXT_NAME,
                'version': TEST_CONTEXT_VERSION,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client,
                                                                     get_context_txn_json)])
    assert rep[0][1]['result']['seqNo']
    assert rep[0][1]['result']['data']['meta'][RS_TYPE] == CONTEXT_TYPE
    assert rep[0][1]['result']['data']['meta'][CONTEXT_NAME] == TEST_CONTEXT_NAME
    assert rep[0][1]['result']['data']['meta'][CONTEXT_VERSION] == TEST_CONTEXT_VERSION
    assert rep[0][1]['result']['data']['data'] == W3C_BASE_CONTEXT


def test_send_get_context_fails_with_invalid_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': "bad_name",
                'version': TEST_CONTEXT_VERSION,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                     get_context_txn_json)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_context_fails_with_incorrect_dest(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, sdk_wallet_client, send_context):
    _, did = sdk_wallet_client
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': CONTEXT_NAME,
                'version': TEST_CONTEXT_VERSION,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                     get_context_txn_json)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_context_fails_with_invalid_dest(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': "wrong_did",
            'meta': {
                'name': CONTEXT_NAME,
                'version': TEST_CONTEXT_VERSION,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                   get_context_txn_json)])
    assert "validation error [ClientGetContextOperation]: should not contain the following chars [\'_\'] (dest=wrong_did)" in str(e.value)


def test_send_get_context_fails_with_incorrect_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': CONTEXT_NAME,
                'version': '2.0',
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                     get_context_txn_json)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_context_fails_with_invalid_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': CONTEXT_NAME,
                'version': 2.0,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                   get_context_txn_json)])
    assert "validation error [GetContextField]: expected types 'str', got 'float' (version=2.0)" in str(e.value)


def test_send_get_context_fails_with_invalid_version_syntax(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': CONTEXT_NAME,
                'version': 'asd',
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                   get_context_txn_json)])
    e.match("Invalid version: 'asd'")


def test_send_get_context_fails_without_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'name': CONTEXT_NAME,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                   get_context_txn_json)])
    e.match('missed fields - version')


def test_send_get_context_fails_without_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'dest': did,
            'meta': {
                'version': CONTEXT_VERSION,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                   get_context_txn_json)])
    e.match('missed fields - name')


def test_send_get_context_fails_without_dest(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_context):
    _, did = sdk_wallet_trustee
    raw_json = {
        'operation': {
            'type': GET_CONTEXT,
            'meta': {
                'name': CONTEXT_NAME,
                'version': CONTEXT_VERSION,
                'type': CONTEXT_TYPE
            }
        },
        "identifier": did,
        "reqId": 12345678,
        "protocolVersion": 2,
    }
    get_context_txn_json = json.dumps(raw_json)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee,
                                                                   get_context_txn_json)])
    e.match('missed fields - dest')
