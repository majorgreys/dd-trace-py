from riot import Suite, Case

global_deps = [
    "mock",
    "pytest<4",
    "opentracing",
]

global_env = [("PYTEST_ADDOPTS", "--color=yes")]

suites = [
    Suite(
        name="black",
        command="black --check .",
        cases=[
            Case(
                pys=[3.8],
                pkgs=[
                    ("black", ["==20.8b1"]),
                ],
            ),
        ],
    ),
    Suite(
        name="flake8",
        command="flake8 ddtrace/ tests/",
        cases=[
            Case(
                pys=[3.8],
                pkgs=[
                    ("flake8", [">=3.8,<3.9"]),
                    ("flake8-blind-except", [""]),
                    ("flake8-builtins", [""]),
                    ("flake8-docstrings", [""]),
                    ("flake8-logging-format", [""]),
                    ("flake8-rst-docstrings", [""]),
                    ("pygments", [""]),
                ],
            ),
        ],
    ),
    Suite(
        name="tracer",
        command="pytest tests/tracer/",
        cases=[
            Case(
                pys=[
                    2.7,
                    3.5,
                    3.6,
                    3.7,
                    3.8,
                    3.9,
                ],
                pkgs=[("msgpack", [""])],
            ),
        ],
    ),
    Suite(
        name="profiling",
        command="python -m tests.profiling.run pytest --capture=no --verbose tests/profiling/",
        env=[
            ("DD_PROFILE_TEST_GEVENT", lambda case: "1" if "gevent" in case.pkgs else None),
        ],
        cases=[
            Case(
                pys=[
                    2.7,
                    3.5,
                    3.6,
                    3.7,
                    3.8,
                    3.9,
                ],
                pkgs=[("gevent", [None, ""]), ("pytest-benchmark", [""])],
            ),
            # Min reqs tests
            Case(
                pys=[2.7],
                pkgs=[
                    ("gevent", ["==1.1.0"]),
                    ("protobuf", ["==3.0.0"]),
                    ("tenacity", ["==5.0.1"]),
                    ("pytest-benchmark", [""]),
                ],
            ),
            Case(
                pys=[
                    3.5,
                    3.6,
                    3.7,
                    3.8,
                    3.9,
                ],
                pkgs=[
                    ("gevent", ["==1.4.0"]),
                    ("protobuf", ["==3.0.0"]),
                    ("tenacity", ["==5.0.1"]),
                    ("pytest-benchmark", [""]),
                ],
            ),
        ],
    ),
    Suite(
        name="pymongo",
        command="pytest tests/contrib/pymongo",
        cases=[
            Case(
                pys=[
                    2.7,
                    3.5,
                    3.6,
                    3.7,
                ],
                pkgs=[
                    (
                        "pymongo",
                        [
                            ">=3.0,<3.1",
                            ">=3.1,<3.2",
                            ">=3.2,<3.3",
                            ">=3.3,<3.4",
                            ">=3.4,<3.5",
                            ">=3.5,<3.6",
                            ">=3.6,<3.7",
                            ">=3.7,<3.8",
                            ">=3.8,<3.9",
                            ">=3.9,<3.10",
                            ">=3.10,<3.11",
                            "",
                        ],
                    ),
                    ("mongoengine", [""]),
                ],
            ),
            Case(
                pys=[
                    3.8,
                    3.9,
                ],
                pkgs=[
                    (
                        "pymongo",
                        [
                            ">=3.0,<3.1",
                            ">=3.1,<3.2",
                            ">=3.2,<3.3",
                            ">=3.3,<3.4",
                            ">=3.5,<3.6",
                            ">=3.6,<3.7",
                            ">=3.7,<3.8",
                            ">=3.8,<3.9",
                            ">=3.9,<3.10",
                            ">=3.10,<3.11",
                            "",
                        ],
                    ),
                    ("mongoengine", [""]),
                ],
            ),
        ],
    ),
]
