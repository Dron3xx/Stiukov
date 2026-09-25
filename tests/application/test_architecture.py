from pytest_archon import archrule


def test_rule_basic():
    (
        archrule("name", comment="some comment")
        .match("pytest_archon.col*")
        .exclude("pytest_archon.colgate")
        .should_not_import("pytest_archon.import_finder")
        .should_import("pytest_archon.core*")
        .check("pytest_archon")
    )


def test_helper_dependencies():
    (
        archrule(
            "helper modules should not import main",
            comment="helper modules must remain independent from the main code"
        )
        .match("app.*")
        .exclude("app.main")
        .exclude("tests*")
        .should_not_import("app.main")
        .check("app")
    )


def test_application_dependencies():
    (
        archrule(
            "application modules should not import test modules",
            comment="application code must remain independent from test code"
        )
        .match("app.*")
        .should_not_import("tests*")
        .should_not_import("run_tests")
        .check("app")
    )