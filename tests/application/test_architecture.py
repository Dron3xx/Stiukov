from pytest_archon import archrule


def test_main_handler_dependencies():
    (
        archrule(
            "Main module may import handlers and voice modules",
            comment="Main module may import handlers and voice modules, but they must not import main"
        )
        .match("app.main")
        .may_import("app.handlers.*")
        .may_import("app.voice.*")
        .should_not_import("app.*")
        .should_not_import("main")
        .check("app.main")
    )


def test_voice_dependencies():
    (
        archrule(
            "Voice modules should not import any other module",
            comment="Voice modules must remain independent from other modules"
        )
        .match("app.voice.*")
        .should_not_import("app.*")
        .should_not_import("main")
        .check("app.voice")
    )


def test_helper_dependencies():
    (
        archrule(
            "Helper modules should not import main",
            comment="Helper modules must remain independent from the main code"
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
            "Application modules should not import test modules",
            comment="Application code must remain independent from test code"
        )
        .match("app.*")
        .should_not_import("tests*")
        .should_not_import("run_tests")
        .check("app")
    )


def test_handlers_dependencies():
    (
        archrule(
            "Handlers modules can import only command and memory modules",
            comment="Handlers code must remain as join module for others"
        )
        .match("app.handlers.*")
        .may_import("app.commands.*")
        .may_import("app.memory.*")
        .should_not_import("app.main")
        .should_not_import("main")
        .check("app.handlers")
    )


def test_commands_dependencies():
    (
        archrule(
            "Commands modules may import only libraries and modules outside of handlers and memory",
            comment="Commands code should not be dependend on importing other modules from handlers and memory "
        )
        .match("app.commands.*")
        .may_import("app.voice.speak")
        .may_import("app.voice.record_audio")
        .should_not_import("app.*")
        .should_not_import("main")
        .check("app.commands")
    )


def test_memory_dependencies():
    (
        archrule(
            "Memory module may import only json and Path from pathlib",
            comment="Memory code should work only on json and Path libraries"
        )
        .match("app.memory.*")
        .should_not_import("app.*")
        .should_not_import("main")
        .check("app.memory")
    )