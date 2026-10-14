import runpy
import sys
import threading
from unittest.mock import Mock, call

import pytest

import common.threads as threads
from fedora_to_cora.person_migrate import MigratePersonResult
from scripts import migrate_persons


@pytest.fixture
def dependencies():
    return {
        "load_environment": Mock(),
        "configure_logging": Mock(),
        "CoraContext": Mock(return_value=Mock()),
        "migrate_person": Mock(
            return_value=MigratePersonResult("CREATED", "person:1", None)
        ),
    }


@pytest.fixture
def cli(monkeypatch, tmp_path, dependencies):
    monkeypatch.setattr(sys, "argv", ["migrate-persons", "--xml-dir", str(tmp_path)])
    for name, dependency in dependencies.items():
        monkeypatch.setattr(migrate_persons, name, dependency)
    monkeypatch.setenv("CORA_WORKERS", "2")
    return tmp_path, dependencies["CoraContext"].return_value


def test_migrates_each_unique_pid_once(cli, capsys, dependencies):
    xml_dir, context = cli
    (xml_dir / "first.xml").write_text(
        "<publication><authors><person>"
        "<authorityPid> authoriy-person:123 </authorityPid>"
        "<authorityPid>authoriy-person:123</authorityPid>"
        "</person></authors><editor><authorityPid>person:456</authorityPid>"
        "</editor><authorityPid/><authorityPid> </authorityPid></publication>"
    )
    (xml_dir / "second.xml").write_text(
        "<publication><authorityPid>person:456</authorityPid></publication>"
    )
    (xml_dir / "ignored.txt").write_text("not XML")
    (xml_dir / "directory.xml").mkdir()
    (xml_dir / "nested").mkdir()
    (xml_dir / "nested" / "ignored.xml").write_text("not XML")

    migrate_persons.main()

    dependencies["migrate_person"].assert_has_calls(
        [call("authoriy-person:123", context), call("person:456", context)],
        any_order=True,
    )
    assert dependencies["migrate_person"].call_count == 2
    output = capsys.readouterr().out
    assert "XML files: 2 | Read: 2 | Failed: 0" in output
    assert "Unique persons: 2" in output
    assert "Created: 2 | Skipped: 0 | Failed: 0" in output


@pytest.mark.parametrize("with_xml", [False, True])
def test_no_persons_does_not_authenticate(cli, capsys, with_xml, dependencies):
    xml_dir, _ = cli
    if with_xml:
        (xml_dir / "empty.xml").write_text("<publication/>")

    migrate_persons.main()

    dependencies["CoraContext"].assert_not_called()
    dependencies["migrate_person"].assert_not_called()
    assert "Unique persons: 0" in capsys.readouterr().out


def test_malformed_xml_does_not_stop_migration(cli, capsys, caplog, dependencies):
    xml_dir, _ = cli
    (xml_dir / "broken.xml").write_text("<publication>")
    (xml_dir / "valid.xml").write_text(
        "<publication><authorityPid>person:1</authorityPid></publication>"
    )

    with pytest.raises(SystemExit) as error:
        migrate_persons.main()

    assert error.value.code == 1
    dependencies["migrate_person"].assert_called_once()
    assert "broken.xml" in caplog.text
    assert "XML files: 2 | Read: 1 | Failed: 1" in capsys.readouterr().out


def test_migration_statuses_and_unexpected_errors(cli, capsys, caplog, dependencies):
    xml_dir, _ = cli
    (xml_dir / "persons.xml").write_text(
        "<publication>"
        + "".join(
            f"<authorityPid>person:{number}</authorityPid>" for number in range(5)
        )
        + "</publication>"
    )

    def migrate(authority_pid, context):
        if authority_pid == "person:0":
            return MigratePersonResult("CREATED", "new:0", None)
        if authority_pid == "person:1":
            return MigratePersonResult("SKIPPED", None, "Already exists")
        if authority_pid == "person:2":
            return MigratePersonResult("FAILED", None, "API rejected person")
        if authority_pid == "person:4":
            return MigratePersonResult("FAILED", None, "API rejected person")
        raise RuntimeError("Unexpected transformation error")

    dependencies["migrate_person"].side_effect = migrate

    with pytest.raises(SystemExit) as error:
        migrate_persons.main()

    assert error.value.code == 1
    assert dependencies["migrate_person"].call_count == 5
    output = capsys.readouterr().out
    assert "Created: 1 | Skipped: 1 | Failed: 3" in output
    assert (
        "Migration errors:\n"
        "  2x API rejected person | authorityPid(s): person:2, person:4\n"
        "  1x Unexpected transformation error | authorityPid(s): person:3" in output
    )
    assert "person:2: API rejected person" in caplog.text
    assert "person:3: Unexpected transformation error" in caplog.text


def test_thread_progress_shows_status_tallies(monkeypatch):
    postfixes = []

    class Progress:
        def __init__(self, iterable):
            self.iterable = iterable

        def __iter__(self):
            return iter(self.iterable)

        def set_postfix_str(self, value):
            postfixes.append(value)

    monkeypatch.setattr(threads, "tqdm", lambda iterable, **kwargs: Progress(iterable))

    results = threads.run_with_threads(
        ["CREATED", "FAILED"],
        lambda status: MigratePersonResult(status, None, None),
        workers=1,
        status_order=[("CREATED", "✅"), ("SKIPPED", "➡️"), ("FAILED", "❌")],
    )

    assert [result.status for result in results] == ["CREATED", "FAILED"]
    assert postfixes == ["✅ 1 | ➡️ 0 | ❌ 0", "✅ 1 | ➡️ 0 | ❌ 1"]


def test_skipped_person_is_success(cli, capsys, dependencies):
    xml_dir, _ = cli
    (xml_dir / "person.xml").write_text(
        "<publication><authorityPid>person:1</authorityPid></publication>"
    )
    dependencies["migrate_person"].return_value = MigratePersonResult(
        "SKIPPED", None, "Already exists"
    )

    migrate_persons.main()

    assert "Created: 0 | Skipped: 1 | Failed: 0" in capsys.readouterr().out


def test_unreadable_xml(monkeypatch, tmp_path, caplog):
    xml_path = tmp_path / "unreadable.xml"
    monkeypatch.setattr(
        migrate_persons, "read_source_xml", Mock(side_effect=PermissionError("Denied"))
    )

    assert migrate_persons._read_authority_pids(xml_path) == (set(), False)
    assert "unreadable.xml" in caplog.text
    assert "Denied" in caplog.text


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--xml-dir", "does-not-exist"],
        ["--workers", "0"],
        ["--workers", "-1"],
        ["--workers", "invalid"],
        ["--apply"],
    ],
)
def test_invalid_arguments(cli, monkeypatch, arguments, dependencies):
    xml_dir, _ = cli
    argv = ["migrate-persons", "--xml-dir", str(xml_dir), *arguments]
    if not arguments:
        argv = ["migrate-persons"]
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as error:
        migrate_persons.main()

    assert error.value.code == 2
    dependencies["CoraContext"].assert_not_called()


def test_xml_dir_cannot_be_a_file(cli, monkeypatch):
    xml_dir, _ = cli
    xml_path = xml_dir / "person.xml"
    xml_path.write_text("<publication/>")
    monkeypatch.setattr(sys, "argv", ["migrate-persons", "--xml-dir", str(xml_path)])

    with pytest.raises(SystemExit) as error:
        migrate_persons.main()

    assert error.value.code == 2


@pytest.mark.parametrize("workers", ["invalid", "0", "-1"])
def test_invalid_environment_workers(cli, monkeypatch, workers):
    monkeypatch.setenv("CORA_WORKERS", workers)

    with pytest.raises(SystemExit) as error:
        migrate_persons.main()

    assert error.value.code == 2


@pytest.mark.parametrize("cli_workers, expected_workers", [(None, 2), ("3", 3)])
def test_forwards_configuration_and_workers(
    cli, monkeypatch, cli_workers, expected_workers, dependencies
):
    xml_dir, _ = cli
    (xml_dir / "person.xml").write_text(
        "<publication><authorityPid>person:1</authorityPid></publication>"
    )
    arguments = [
        "migrate-persons",
        "--xml-dir",
        str(xml_dir),
        "--system",
        "preview",
        "--login-id",
        "test-user",
        "--app-token",
        "test-token",
        "--cora-url",
        "https://example.org",
    ]
    if cli_workers is not None:
        arguments.extend(["--workers", cli_workers])
    monkeypatch.setattr(sys, "argv", arguments)
    run_with_threads = Mock(wraps=migrate_persons.run_with_threads)
    monkeypatch.setattr(migrate_persons, "run_with_threads", run_with_threads)

    migrate_persons.main()

    dependencies["CoraContext"].assert_called_once_with(
        system="preview",
        login_id="test-user",
        app_token="test-token",
        workers=expected_workers,
        cora_url="https://example.org",
    )
    assert run_with_threads.call_count == 2
    assert all(
        invocation.kwargs["workers"] == expected_workers
        for invocation in run_with_threads.call_args_list
    )
    dependencies["load_environment"].assert_called_once_with()
    dependencies["configure_logging"].assert_called_once_with()


def test_migrates_concurrently(cli, dependencies):
    xml_dir, _ = cli
    (xml_dir / "persons.xml").write_text(
        "<publication><authorityPid>person:1</authorityPid>"
        "<authorityPid>person:2</authorityPid></publication>"
    )
    barrier = threading.Barrier(2, timeout=5)

    def migrate(authority_pid, context):
        barrier.wait()
        return MigratePersonResult("CREATED", authority_pid, None)

    dependencies["migrate_person"].side_effect = migrate

    migrate_persons.main()

    assert dependencies["migrate_person"].call_count == 2


def test_authentication_failure(cli, capsys, dependencies):
    xml_dir, _ = cli
    (xml_dir / "person.xml").write_text(
        "<publication><authorityPid>person:1</authorityPid></publication>"
    )
    dependencies["CoraContext"].side_effect = RuntimeError("Login failed")

    with pytest.raises(SystemExit) as error:
        migrate_persons.main()

    assert error.value.code == 1
    assert "Failed to initialize Cora context: Login failed" in capsys.readouterr().err
    dependencies["migrate_person"].assert_not_called()


def test_module_entrypoint(cli, monkeypatch, capsys):
    monkeypatch.setattr("common.environment.load_environment", Mock())
    monkeypatch.setattr("common.logging_config.configure_logging", Mock())
    monkeypatch.delitem(sys.modules, "scripts.migrate_persons")

    runpy.run_module("scripts.migrate_persons", run_name="__main__")

    assert "Unique persons: 0" in capsys.readouterr().out
