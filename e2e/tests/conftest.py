import pytest

from support import run_compose, wait_for_frontend, wait_for_json


@pytest.fixture(scope="session", autouse=True)
def compose_stack() -> None:
    run_compose("down", "-v", check=False)
    run_compose("up", "--build", "-d", "--scale", "agent=0")
    wait_for_json("/health")
    wait_for_frontend()

    yield

    run_compose("down", "-v", check=False)
