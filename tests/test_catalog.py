from app.catalog import load_catalog, tools_by_category


EXPECTED_REPOS = {
    "https://github.com/kdave/btrfs-progs",
    "https://github.com/digint/btrbk",
    "https://github.com/kdave/btrfsmaintenance",
    "https://github.com/Zygo/bees",
    "https://github.com/markfasheh/duperemove",
    "https://github.com/AnotherStranger/duperemove-timer",
    "https://github.com/ximion/btrfsd",
    "https://github.com/maharmstone/ntfs2btrfs",
    "https://github.com/knorrie/btrfs-heatmap",
    "https://github.com/automorphism88/snapraid-btrfs",
    "https://github.com/AmesCornish/buttersink",
    "https://github.com/CyberShadow/btdu",
    "https://github.com/danthem/undelete-btrfs",
    "https://github.com/egara/buttermanager",
    "https://github.com/davispuh/btrfs-data-recovery",
    "https://github.com/NETWAYS/check_disk_btrfs",
    "https://github.com/boredsquirrel/awesome-btrfs",
}


def test_catalog_includes_all_required_repos() -> None:
    catalog = load_catalog()
    repos = {tool.repo for tool in catalog.tools}
    missing = EXPECTED_REPOS - repos
    assert not missing, f"Missing repositories: {sorted(missing)}"


def test_btrfs_progs_coverage_has_key_areas() -> None:
    catalog = load_catalog()
    all_commands = {cmd for area in catalog.functional_areas for cmd in area.commands}

    for command in ["filesystem", "device", "balance", "scrub", "send", "receive", "rescue", "check"]:
        assert command in all_commands


def test_navigation_and_grouping_non_empty() -> None:
    catalog = load_catalog()
    grouped = tools_by_category(catalog)

    assert len(catalog.navigation) >= 6
    assert grouped
    assert "RAID & Layout" in grouped
