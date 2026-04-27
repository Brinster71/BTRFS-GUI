"""Administrative operations for BTRFS mission control."""

from __future__ import annotations

from dataclasses import dataclass
import os
import shlex
import subprocess
from typing import Callable


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    placeholder: str = ""
    required: bool = True


@dataclass(frozen=True)
class Operation:
    key: str
    title: str
    description: str
    command_family: str
    destructive: bool
    fields: list[Field]
    builder: Callable[[dict[str, str]], list[str]]


@dataclass(frozen=True)
class OperationResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    blocked: bool = False
    block_reason: str = ""


def _required(params: dict[str, str], key: str) -> str:
    value = params.get(key, "").strip()
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value


def _optional(params: dict[str, str], key: str, default: str = "") -> str:
    return params.get(key, default).strip()


def build_create_filesystem(params: dict[str, str]) -> list[str]:
    device = _required(params, "device")
    label = _optional(params, "label")
    data_profile = _optional(params, "data_profile", "single")
    metadata_profile = _optional(params, "metadata_profile", "dup")

    cmd = ["mkfs.btrfs", "-d", data_profile, "-m", metadata_profile]
    if label:
        cmd += ["-L", label]
    cmd.append(device)
    return cmd


def build_balance_start(params: dict[str, str]) -> list[str]:
    mountpoint = _required(params, "mountpoint")
    data = _optional(params, "data_profile")
    metadata = _optional(params, "metadata_profile")

    cmd = ["btrfs", "balance", "start"]
    filters: list[str] = []
    if data:
        filters.append(f"dconvert={data}")
    if metadata:
        filters.append(f"mconvert={metadata}")
    for item in filters:
        cmd += ["-d", item] if item.startswith("dconvert") else ["-m", item]
    cmd.append(mountpoint)
    return cmd


def build_scrub_start(params: dict[str, str]) -> list[str]:
    mountpoint = _required(params, "mountpoint")
    return ["btrfs", "scrub", "start", "-B", mountpoint]


def build_subvolume_snapshot(params: dict[str, str]) -> list[str]:
    source = _required(params, "source")
    dest = _required(params, "destination")
    readonly = _optional(params, "readonly", "false").lower() == "true"
    cmd = ["btrfs", "subvolume", "snapshot"]
    if readonly:
        cmd.append("-r")
    cmd += [source, dest]
    return cmd


def build_quota_enable(params: dict[str, str]) -> list[str]:
    mountpoint = _required(params, "mountpoint")
    return ["btrfs", "quota", "enable", mountpoint]


def build_device_add(params: dict[str, str]) -> list[str]:
    device = _required(params, "device")
    mountpoint = _required(params, "mountpoint")
    return ["btrfs", "device", "add", device, mountpoint]


def build_device_remove(params: dict[str, str]) -> list[str]:
    device = _required(params, "device")
    mountpoint = _required(params, "mountpoint")
    return ["btrfs", "device", "remove", device, mountpoint]


def build_filesystem_resize(params: dict[str, str]) -> list[str]:
    size = _required(params, "size")
    mountpoint = _required(params, "mountpoint")
    return ["btrfs", "filesystem", "resize", size, mountpoint]


def build_check_readonly(params: dict[str, str]) -> list[str]:
    device = _required(params, "device")
    return ["btrfs", "check", "--readonly", device]


def build_restore(params: dict[str, str]) -> list[str]:
    source = _required(params, "source_device")
    destination = _required(params, "destination_dir")
    return ["btrfs", "restore", source, destination]


def build_send(params: dict[str, str]) -> list[str]:
    subvol = _required(params, "subvolume")
    target_file = _required(params, "target_file")
    return ["sh", "-lc", f"btrfs send {shlex.quote(subvol)} > {shlex.quote(target_file)}"]


def build_receive(params: dict[str, str]) -> list[str]:
    stream_file = _required(params, "stream_file")
    destination = _required(params, "destination")
    return ["sh", "-lc", f"cat {shlex.quote(stream_file)} | btrfs receive {shlex.quote(destination)}"]


OPERATIONS: list[Operation] = [
    Operation(
        key="create_filesystem",
        title="Create BTRFS Filesystem",
        description="Initialize a device with mkfs.btrfs and profile options.",
        command_family="File System Creation",
        destructive=True,
        fields=[
            Field("device", "Device path", "/dev/sdb"),
            Field("label", "Label", "data-pool", required=False),
            Field("data_profile", "Data profile", "single"),
            Field("metadata_profile", "Metadata profile", "dup"),
        ],
        builder=build_create_filesystem,
    ),
    Operation(
        key="balance_raid",
        title="Balance / RAID Profile Convert",
        description="Convert mounted filesystem chunk profiles via btrfs balance.",
        command_family="Raid setup",
        destructive=True,
        fields=[
            Field("mountpoint", "Mount point", "/mnt/btrfs"),
            Field("data_profile", "Target data profile", "raid1"),
            Field("metadata_profile", "Target metadata profile", "raid1"),
        ],
        builder=build_balance_start,
    ),
    Operation(
        key="scrub",
        title="Scrub Filesystem",
        description="Run blocking scrub and return health output.",
        command_family="Maintenance",
        destructive=False,
        fields=[Field("mountpoint", "Mount point", "/mnt/btrfs")],
        builder=build_scrub_start,
    ),
    Operation(
        key="snapshot",
        title="Create Snapshot",
        description="Create writable or readonly subvolume snapshot.",
        command_family="Subvolume",
        destructive=False,
        fields=[
            Field("source", "Source subvolume", "/mnt/btrfs/@"),
            Field("destination", "Snapshot destination", "/mnt/btrfs/.snapshots/@-now"),
            Field("readonly", "Readonly (true/false)", "true", required=False),
        ],
        builder=build_subvolume_snapshot,
    ),
    Operation(
        key="quota_enable",
        title="Enable Quotas",
        description="Enable qgroup accounting on a mounted filesystem.",
        command_family="Quota",
        destructive=False,
        fields=[Field("mountpoint", "Mount point", "/mnt/btrfs")],
        builder=build_quota_enable,
    ),
    Operation(
        key="device_add",
        title="Add Device",
        description="Add a device to existing filesystem.",
        command_family="Device",
        destructive=True,
        fields=[
            Field("device", "Device path", "/dev/sdc"),
            Field("mountpoint", "Mount point", "/mnt/btrfs"),
        ],
        builder=build_device_add,
    ),
    Operation(
        key="device_remove",
        title="Remove Device",
        description="Remove device from mounted filesystem.",
        command_family="Device",
        destructive=True,
        fields=[
            Field("device", "Device path", "/dev/sdc"),
            Field("mountpoint", "Mount point", "/mnt/btrfs"),
        ],
        builder=build_device_remove,
    ),
    Operation(
        key="resize",
        title="Resize Filesystem",
        description="Resize mounted filesystem (e.g., +10G, max).",
        command_family="Filesystem",
        destructive=True,
        fields=[
            Field("size", "Resize value", "+10G"),
            Field("mountpoint", "Mount point", "/mnt/btrfs"),
        ],
        builder=build_filesystem_resize,
    ),
    Operation(
        key="check",
        title="Readonly Integrity Check",
        description="Perform a safe readonly btrfs check.",
        command_family="Check",
        destructive=False,
        fields=[Field("device", "Device path", "/dev/sdb")],
        builder=build_check_readonly,
    ),
    Operation(
        key="restore",
        title="Restore Extract",
        description="Extract recoverable files from damaged filesystem.",
        command_family="Rescue",
        destructive=False,
        fields=[
            Field("source_device", "Source device", "/dev/sdb"),
            Field("destination_dir", "Destination directory", "/tmp/recover"),
        ],
        builder=build_restore,
    ),
    Operation(
        key="send",
        title="Send Snapshot to File",
        description="Create send-stream file from a snapshot.",
        command_family="Send/Receive",
        destructive=False,
        fields=[
            Field("subvolume", "Snapshot path", "/mnt/btrfs/.snapshots/snap1"),
            Field("target_file", "Stream output file", "/tmp/snap1.stream"),
        ],
        builder=build_send,
    ),
    Operation(
        key="receive",
        title="Receive Stream",
        description="Apply a stream file into destination filesystem.",
        command_family="Send/Receive",
        destructive=False,
        fields=[
            Field("stream_file", "Stream input file", "/tmp/snap1.stream"),
            Field("destination", "Destination path", "/mnt/backup"),
        ],
        builder=build_receive,
    ),
]


def get_operation(key: str) -> Operation:
    for op in OPERATIONS:
        if op.key == key:
            return op
    raise KeyError(f"Unknown operation: {key}")


def run_operation(operation: Operation, params: dict[str, str], dry_run: bool = True) -> OperationResult:
    command = operation.builder(params)
    command_text = " ".join(shlex.quote(part) for part in command)

    if dry_run:
        return OperationResult(command=command_text, returncode=0, stdout="Dry run: command not executed.", stderr="")

    allow_destructive = os.getenv("BTRFS_GUI_ALLOW_DESTRUCTIVE", "false").lower() == "true"
    if operation.destructive and not allow_destructive:
        return OperationResult(
            command=command_text,
            returncode=126,
            stdout="",
            stderr="Execution blocked.",
            blocked=True,
            block_reason="Set BTRFS_GUI_ALLOW_DESTRUCTIVE=true to run destructive operations.",
        )

    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return OperationResult(
        command=command_text,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
