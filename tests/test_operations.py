import os

from app.operations import get_operation, run_operation


def test_create_filesystem_command_builds() -> None:
    op = get_operation("create_filesystem")
    result = run_operation(
        op,
        {
            "device": "/dev/sdz",
            "label": "pool",
            "data_profile": "raid1",
            "metadata_profile": "raid1",
        },
        dry_run=True,
    )
    assert "mkfs.btrfs" in result.command
    assert "-L" in result.command
    assert "/dev/sdz" in result.command


def test_destructive_execution_blocked_without_env() -> None:
    op = get_operation("resize")
    os.environ.pop("BTRFS_GUI_ALLOW_DESTRUCTIVE", None)
    result = run_operation(
        op,
        {"size": "+1G", "mountpoint": "/mnt/test"},
        dry_run=False,
    )
    assert result.blocked is True
    assert result.returncode == 126


def test_non_destructive_runs_in_dry_mode() -> None:
    op = get_operation("scrub")
    result = run_operation(op, {"mountpoint": "/mnt/test"}, dry_run=True)
    assert result.returncode == 0
    assert "Dry run" in result.stdout


def test_missing_required_fields_raise() -> None:
    op = get_operation("device_add")
    try:
        run_operation(op, {"device": "", "mountpoint": "/mnt/test"}, dry_run=True)
    except ValueError as exc:
        assert "device" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing required field")
