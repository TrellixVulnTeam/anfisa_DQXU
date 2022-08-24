import json
import pytest
import time

from csvvalidator import CSVValidator
from lib.api.adm_drop_ds_api import AdmDropDs
from lib.api.dirinfo_api import DirInfo
from lib.schemas.csv_export_schema import csv_export_schema
from lib.api.dsinfo_api import Dsinfo
from lib.schemas.common import enum_property_status, numeric_property_status, func_property_status
from lib.schemas.dtree_stat_schema import dtree_stat_schema
from tests.helpers.generators import testDataPrefix, Generator
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_TYPES
from jsonschema import validate
from pytest_bdd import parsers, given, then
from lib.api.ds2ws_api import Ds2ws
from lib.api.job_status_api import JobStatus
from tests.helpers.constructors import Constructor
from deepdiff import DeepDiff
from lib.schemas.ds2ws_schema import ds2ws_schema
from lib.schemas.dsinfo_schema import dsinfo_schema
from lib.schemas.dtree_check_schema import dtree_check_schema


# Hooks
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    print(f'Step failed: {step}')


def pytest_bdd_after_scenario():
    ws_to_drop = []
    response = DirInfo.get()
    ds_dict = json.loads(response.content)["ds-dict"]
    for value in ds_dict.values():
        try:
            if testDataPrefix + 'ws' in value['name']:
                ws_to_drop.append(value['name'])
        except ValueError:
            continue
        except TypeError:
            continue
    for wsDataset in ws_to_drop:
        time.sleep(1)
        AdmDropDs.post({'ds': wsDataset})


# Fixtures
@pytest.fixture
def fixture_function():
    print('fixture_function')


# Shared Given Steps
@given('I do something', target_fixture='ddg_home')
def i_do_something(fixture_function):
    print('i_do_something')


def successful_string_to_bool(successful):
    if successful == "successful":
        return True
    else:
        return False


def number_of_ds_records(ds_name):
    response = Dsinfo.get({'ds': ds_name})
    return response.json()['total']


def xl_dataset(required_records=0):
    _dataset = ''
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.content)["ds-dict"]
    for value in ds_dict.values():
        if (value['kind'] == 'xl') and (number_of_ds_records(value['name']) > required_records):
            _dataset = value['name']
            break
    assert _dataset != ''
    return _dataset


def find_dataset(dataset):
    found = False
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.content)["ds-dict"]
    for value in ds_dict.values():
        if value['name'] == dataset:
            found = True
            break
    assert found


def ds_creation_status(task_id):
    parameters = {'task': task_id}
    job_status_response = JobStatus.post(parameters)
    for i in range(10):
        if (job_status_response.json()[1] == 'Done') or (job_status_response.json()[0] is None):
            break
        else:
            time.sleep(1)
            job_status_response = JobStatus.post(parameters)
            continue
    return job_status_response.json()[1]


def derive_ws(dataset):
    # Deriving ws dataset
    unique_ws_name = Generator.unique_name('ws')
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name, code='return False')
    response = Ds2ws.post(parameters)

    # Checking creation
    assert ds_creation_status(response.json()['task_id']) == 'Done'
    return unique_ws_name


@given(
    parsers.cfparse('{dataset_identifier:String} is uploaded and processed by the system',
                    extra_types=EXTRA_STRING_TYPES), target_fixture='dataset')
def dataset(dataset_identifier):
    match dataset_identifier:
        case 'xl Dataset':
            return xl_dataset()
        case 'xl Dataset with > 9000 records':
            return xl_dataset(9000)
        case 'ws Dataset':
            return derive_ws(xl_dataset())
        case _:
            find_dataset(dataset_identifier)
            return dataset_identifier


@then(parsers.cfparse('response body schema should be valid by "{schema:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_json_schema(schema):
    print(schema)
    match schema:
        case 'dsinfo_schema':
            validate(pytest.response.json(), dsinfo_schema)
        case 'dtree_check_schema':
            validate(pytest.response.json(), dtree_check_schema)
        case 'ds2ws_schema':
            validate(pytest.response.json(), ds2ws_schema)
        case 'dtree_stat_schema':
            validate(pytest.response.json(), dtree_stat_schema)
        case 'csv_export_schema':
            validator = CSVValidator(csv_export_schema)
            validator.add_value_check('chromosome', str)
            validator.add_value_check('variant', str)
            problems = validator.validate(pytest.response.text)
            assert len(problems) == 0
        case _:
            print(f"Sorry, I couldn't understand {schema!r}")


@then(parsers.cfparse('response body "{key:String}" should be equal {value:String}', extra_types=EXTRA_STRING_TYPES))
def assert_response_code(key, value):
    response_json = json.loads(pytest.response.text)
    assert response_json[key] == value


@then(parsers.cfparse('response body should contain "{error_message:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(error_message):
    assert error_message in pytest.response.text


@then(parsers.cfparse('response body should be equal "{body:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(body):
    assert pytest.response.text == f'"{body}"'


@then(parsers.cfparse('response status should be {status:Number} {text:String}', extra_types=EXTRA_TYPES))
def assert_status(status, text):
    assert pytest.response.status_code == status


@then(parsers.cfparse('response body {property_name:String} property_status schemas should be valid',
                      extra_types=EXTRA_STRING_TYPES))
def assert_stat_list_schemas(property_name):
    for element in pytest.response.json()[property_name]:
        match element['kind']:
            case 'enum':
                validate(element, enum_property_status)
            case 'numeric':
                validate(element, numeric_property_status)
            case 'func':
                validate(element, func_property_status)


@then(parsers.cfparse('response body json should match expected data for {request_name:String} request',
                      extra_types=EXTRA_STRING_TYPES))
def assert_json_data(request_name, dataset):
    with open(f'tests/test_data/{dataset}/{request_name}.json', encoding="utf8") as f:
        test_data_json = json.load(f)
    response_json = json.loads(pytest.response.text)

    print('\ntest_data_json\n', json.dumps(test_data_json, indent=4, sort_keys=True))
    print('\nresponse_json\n', json.dumps(response_json, indent=4, sort_keys=True))

    ddiff = DeepDiff(test_data_json, response_json, ignore_order=True, exclude_paths={"root['rq-id']"})
    print('ddiff', ddiff)

    assert ddiff == {}


@then(parsers.cfparse('response body should match expected data for "{request_name:String}" request',
                      extra_types=EXTRA_STRING_TYPES))
def assert_csv_data(request_name, dataset):
    with open(f'tests/test_data/xl_PGP3140_wgs_NIST-3_3_2/ws_callers_in_GATK_HOMOZYGOUS/{request_name}', encoding="utf8") as f:
        file = f.read()
    print('file\n\n',file)
