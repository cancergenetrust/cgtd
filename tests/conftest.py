import os
import sys
import pytest


sys.path.append(os.path.join(os.getcwd(), '.'))
sys.path.append(os.path.join(os.getcwd(), '..'))


def pytest_addoption(parser):
    parser.addoption("--server", action="store",
                     dest='server', default='http://127.0.0.1:5000',
                     help="Test server url")


@pytest.fixture
def server(request):
    return request.config.getoption("--server")


def pytest_runtest_setup(item):
    pass
