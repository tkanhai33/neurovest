#!/usr/bin/env python3

"""
Phase 136 Stage 1 hardware and platform discovery.

All inspection is read-only.

The scanner does not:

- execute NeuroVest
- start services
- stop services
- modify system configuration
- change CPU governors
- run stress tests
- write to storage devices
- connect to external providers
"""

from __future__ import annotations

import os
import platform
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.phase136.utils.command_runner import (
    run_command,
    run_json_command,
    version_command,
)


class HardwarePlatformScanner:
    """
    Discover workstation hardware, software, and service evidence.
    """

    def __init__(
        self,
        repository_root: Path,
    ) -> None:
        self.repository_root = repository_root.resolve()

    def scan(self) -> dict[str, Any]:
        started_at = datetime.now(UTC)

        cpu = self._scan_cpu()
        memory = self._scan_memory()
        motherboard = self._scan_motherboard()
        gpu = self._scan_gpu()
        storage = self._scan_storage()
        filesystems = self._scan_filesystems()
        network = self._scan_network()
        sensors = self._scan_sensors()
        operating_system = self._scan_operating_system()
        software = self._scan_software()
        services = self._scan_services()
        virtualization = self._scan_virtualization()
        repository = self._scan_repository()
        resource_snapshot = self._scan_resource_snapshot()

        completed_at = datetime.now(UTC)

        limitations = self._build_limitations(
            motherboard=motherboard,
            sensors=sensors,
            storage=storage,
        )

        return {
            "phase": 136,
            "stage": 1,
            "stage_name": (
                "Hardware and Platform Discovery"
            ),
            "inspection_mode": "read_only",
            "application_executed": False,
            "application_modified": False,
            "stress_test_executed": False,
            "external_network_test_executed": False,
            "deployment_approved": False,
            "live_trading_approved": False,
            "status": "completed",
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": round(
                (
                    completed_at
                    - started_at
                ).total_seconds(),
                6,
            ),
            "repository_root": str(
                self.repository_root
            ),
            "hardware": {
                "cpu": cpu,
                "memory": memory,
                "motherboard": motherboard,
                "gpu": gpu,
                "storage": storage,
                "filesystems": filesystems,
                "network": network,
                "sensors": sensors,
            },
            "platform": {
                "operating_system": operating_system,
                "software": software,
                "services": services,
                "virtualization": virtualization,
                "repository": repository,
            },
            "resource_snapshot": resource_snapshot,
            "summary": self._build_summary(
                cpu=cpu,
                memory=memory,
                gpu=gpu,
                storage=storage,
                network=network,
                sensors=sensors,
                software=software,
                services=services,
            ),
            "limitations": limitations,
        }

    def _scan_cpu(self) -> dict[str, Any]:
        lscpu = run_json_command(
            ["lscpu", "-J"]
        )

        fields: dict[str, str] = {}

        payload = lscpu.get("json")

        if isinstance(payload, dict):
            for item in payload.get(
                "lscpu",
                [],
            ):
                field = str(
                    item.get("field", "")
                ).rstrip(":")

                data = str(
                    item.get("data", "")
                )

                if field:
                    fields[field] = data

        frequency = self._read_cpu_frequency()
        governors = self._read_cpu_governors()
        vulnerabilities = self._read_cpu_vulnerabilities()

        return {
            "command_result": lscpu,
            "fields": fields,
            "model_name": fields.get(
                "Model name"
            ),
            "architecture": fields.get(
                "Architecture"
            ),
            "physical_cores": self._int_value(
                fields.get(
                    "Core(s) per socket"
                )
            ),
            "sockets": self._int_value(
                fields.get("Socket(s)")
            ),
            "logical_cpus": self._int_value(
                fields.get("CPU(s)")
            ),
            "threads_per_core": self._int_value(
                fields.get(
                    "Thread(s) per core"
                )
            ),
            "max_mhz": self._float_value(
                fields.get("CPU max MHz")
            ),
            "min_mhz": self._float_value(
                fields.get("CPU min MHz")
            ),
            "l1d_cache": fields.get(
                "L1d cache"
            ),
            "l1i_cache": fields.get(
                "L1i cache"
            ),
            "l2_cache": fields.get(
                "L2 cache"
            ),
            "l3_cache": fields.get(
                "L3 cache"
            ),
            "virtualization": fields.get(
                "Virtualization"
            ),
            "current_frequency": frequency,
            "governors": governors,
            "vulnerabilities": vulnerabilities,
        }

    def _scan_memory(self) -> dict[str, Any]:
        meminfo = self._parse_key_value_file(
            Path("/proc/meminfo"),
            separator=":",
        )

        free = run_command(
            ["free", "-b"]
        )

        total_bytes = self._meminfo_bytes(
            meminfo.get("MemTotal")
        )

        available_bytes = self._meminfo_bytes(
            meminfo.get("MemAvailable")
        )

        swap_total_bytes = self._meminfo_bytes(
            meminfo.get("SwapTotal")
        )

        swap_free_bytes = self._meminfo_bytes(
            meminfo.get("SwapFree")
        )

        dimm_scan = run_command(
            [
                "sudo",
                "-n",
                "dmidecode",
                "--type",
                "memory",
            ]
        )

        return {
            "total_bytes": total_bytes,
            "total_gib": self._bytes_to_gib(
                total_bytes
            ),
            "available_bytes": available_bytes,
            "available_gib": self._bytes_to_gib(
                available_bytes
            ),
            "swap_total_bytes": swap_total_bytes,
            "swap_total_gib": self._bytes_to_gib(
                swap_total_bytes
            ),
            "swap_free_bytes": swap_free_bytes,
            "swap_free_gib": self._bytes_to_gib(
                swap_free_bytes
            ),
            "free_command": free,
            "dimm_scan": dimm_scan,
            "dimm_details_available": (
                dimm_scan.get("status")
                == "success"
            ),
        }

    def _scan_motherboard(self) -> dict[str, Any]:
        board = {
            "vendor": self._read_text_file(
                Path(
                    "/sys/class/dmi/id/"
                    "board_vendor"
                )
            ),
            "name": self._read_text_file(
                Path(
                    "/sys/class/dmi/id/"
                    "board_name"
                )
            ),
            "version": self._read_text_file(
                Path(
                    "/sys/class/dmi/id/"
                    "board_version"
                )
            ),
            "bios_vendor": self._read_text_file(
                Path(
                    "/sys/class/dmi/id/"
                    "bios_vendor"
                )
            ),
            "bios_version": self._read_text_file(
                Path(
                    "/sys/class/dmi/id/"
                    "bios_version"
                )
            ),
            "bios_date": self._read_text_file(
                Path(
                    "/sys/class/dmi/id/"
                    "bios_date"
                )
            ),
            "product_name": self._read_text_file(
                Path(
                    "/sys/class/dmi/id/"
                    "product_name"
                )
            ),
        }

        dmidecode = run_command(
            [
                "sudo",
                "-n",
                "dmidecode",
                "--type",
                "baseboard",
                "--type",
                "bios",
            ]
        )

        board["dmidecode"] = dmidecode
        board["privileged_details_available"] = (
            dmidecode.get("status")
            == "success"
        )

        return board

    def _scan_gpu(self) -> dict[str, Any]:
        lspci = run_command(
            ["lspci", "-nnk"]
        )

        pci_gpu_lines = []

        if lspci.get("stdout"):
            lines = lspci["stdout"].splitlines()

            for index, line in enumerate(lines):
                lowered = line.lower()

                if (
                    "vga compatible controller"
                    in lowered
                    or "3d controller" in lowered
                    or "display controller"
                    in lowered
                ):
                    block = [line]

                    for following in lines[
                        index + 1:index + 5
                    ]:
                        if following.startswith(
                            "\t"
                        ):
                            block.append(following)
                        else:
                            break

                    pci_gpu_lines.append(
                        "\n".join(block)
                    )

        nvidia = run_command(
            [
                "nvidia-smi",
                "--query-gpu="
                "name,memory.total,"
                "driver_version,"
                "temperature.gpu,"
                "power.limit",
                "--format=csv,noheader,nounits",
            ]
        )

        amd_sysfs = self._scan_amd_gpu_sysfs()

        return {
            "pci_devices": pci_gpu_lines,
            "lspci": lspci,
            "nvidia": {
                "detected": (
                    nvidia.get("status")
                    == "success"
                ),
                "command_result": nvidia,
            },
            "amd": amd_sysfs,
            "detected_vendor": self._detect_gpu_vendor(
                pci_gpu_lines
            ),
        }

    def _scan_storage(self) -> dict[str, Any]:
        lsblk = run_json_command(
            [
                "lsblk",
                "-J",
                "-b",
                "-O",
            ],
            timeout=30,
        )

        nvme_list = run_json_command(
            [
                "nvme",
                "list",
                "-o",
                "json",
            ]
        )

        smart_devices = run_json_command(
            [
                "smartctl",
                "--scan-open",
                "--json",
            ]
        )

        devices = []

        payload = lsblk.get("json")

        if isinstance(payload, dict):
            for device in payload.get(
                "blockdevices",
                [],
            ):
                if device.get("type") not in {
                    "disk",
                    "nvme",
                }:
                    continue

                devices.append(
                    {
                        "name": device.get("name"),
                        "path": device.get("path"),
                        "model": device.get("model"),
                        "serial": device.get("serial"),
                        "size_bytes": device.get("size"),
                        "size_gib": self._bytes_to_gib(
                            device.get("size")
                        ),
                        "transport": device.get(
                            "tran"
                        ),
                        "rotational": device.get(
                            "rota"
                        ),
                        "scheduler": device.get(
                            "sched"
                        ),
                        "read_only": device.get(
                            "ro"
                        ),
                        "state": device.get(
                            "state"
                        ),
                        "mountpoints": device.get(
                            "mountpoints"
                        ),
                    }
                )

        return {
            "devices": devices,
            "device_count": len(devices),
            "lsblk": lsblk,
            "nvme_list": nvme_list,
            "smart_device_scan": smart_devices,
            "destructive_test_executed": False,
            "benchmark_executed": False,
        }

    def _scan_filesystems(self) -> dict[str, Any]:
        df = run_command(
            [
                "df",
                "-B1",
                "--output="
                "source,fstype,size,used,"
                "avail,pcent,target",
            ]
        )

        rows = []

        if df.get("stdout"):
            lines = df["stdout"].splitlines()

            for line in lines[1:]:
                parts = line.split(
                    maxsplit=6
                )

                if len(parts) != 7:
                    continue

                source, fstype, size, used, available, percent, target = parts

                rows.append(
                    {
                        "source": source,
                        "filesystem": fstype,
                        "size_bytes": self._int_value(
                            size
                        ),
                        "used_bytes": self._int_value(
                            used
                        ),
                        "available_bytes": self._int_value(
                            available
                        ),
                        "used_percent": percent,
                        "mountpoint": target,
                    }
                )

        root_row = next(
            (
                row
                for row in rows
                if row["mountpoint"] == "/"
            ),
            None,
        )

        return {
            "filesystems": rows,
            "root_filesystem": root_row,
            "df": df,
        }

    def _scan_network(self) -> dict[str, Any]:
        addresses = run_json_command(
            [
                "ip",
                "-j",
                "address",
            ]
        )

        routes = run_json_command(
            [
                "ip",
                "-j",
                "route",
            ]
        )

        links = run_json_command(
            [
                "ip",
                "-j",
                "-s",
                "link",
            ]
        )

        ethtool_interfaces = []

        address_payload = addresses.get(
            "json"
        )

        if isinstance(address_payload, list):
            for interface in address_payload:
                name = interface.get(
                    "ifname"
                )

                if not name or name == "lo":
                    continue

                ethtool = run_command(
                    [
                        "ethtool",
                        name,
                    ]
                )

                ethtool_interfaces.append(
                    {
                        "interface": name,
                        "result": ethtool,
                    }
                )

        active_interfaces = []

        if isinstance(address_payload, list):
            for interface in address_payload:
                flags = interface.get(
                    "flags",
                    [],
                )

                if (
                    interface.get("ifname")
                    != "lo"
                    and "UP" in flags
                ):
                    active_interfaces.append(
                        interface.get("ifname")
                    )

        return {
            "addresses": addresses,
            "routes": routes,
            "links": links,
            "active_interfaces": sorted(
                active_interfaces
            ),
            "ethtool": ethtool_interfaces,
            "external_speed_test_executed": False,
        }

    def _scan_sensors(self) -> dict[str, Any]:
        sensors_json = run_json_command(
            [
                "sensors",
                "-j",
            ]
        )

        sensors_text = run_command(
            ["sensors"]
        )

        temperatures = self._extract_temperatures(
            sensors_json.get("json")
        )

        fan_speeds = self._extract_fan_speeds(
            sensors_json.get("json")
        )

        return {
            "available": (
                sensors_text.get("status")
                == "success"
            ),
            "json_result": sensors_json,
            "text_result": sensors_text,
            "temperatures_celsius": temperatures,
            "fan_speeds_rpm": fan_speeds,
            "temperature_count": len(
                temperatures
            ),
            "fan_sensor_count": len(
                fan_speeds
            ),
        }

    def _scan_operating_system(
        self,
    ) -> dict[str, Any]:
        os_release = self._parse_key_value_file(
            Path("/etc/os-release"),
            separator="=",
        )

        uname = run_command(
            ["uname", "-a"]
        )

        hostname = run_command(
            ["hostnamectl"]
        )

        uptime = run_command(
            ["uptime", "-p"]
        )

        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_runtime": platform.python_version(),
            "os_release": os_release,
            "uname": uname,
            "hostnamectl": hostname,
            "uptime": uptime,
        }

    def _scan_software(self) -> dict[str, Any]:
        software = [
            version_command(
                "python",
                [
                    ["python3", "--version"],
                    ["python", "--version"],
                ],
            ),
            version_command(
                "pip",
                [
                    ["pip3", "--version"],
                    ["pip", "--version"],
                ],
            ),
            version_command(
                "node",
                [
                    ["node", "--version"],
                ],
            ),
            version_command(
                "npm",
                [
                    ["npm", "--version"],
                ],
            ),
            version_command(
                "git",
                [
                    ["git", "--version"],
                ],
            ),
            version_command(
                "docker",
                [
                    ["docker", "--version"],
                ],
            ),
            version_command(
                "docker_compose",
                [
                    [
                        "docker",
                        "compose",
                        "version",
                    ],
                    [
                        "docker-compose",
                        "--version",
                    ],
                ],
            ),
            version_command(
                "postgres_client",
                [
                    ["psql", "--version"],
                ],
            ),
            version_command(
                "postgres_server",
                [
                    ["postgres", "--version"],
                ],
            ),
            version_command(
                "ollama",
                [
                    ["ollama", "--version"],
                ],
            ),
            version_command(
                "sensors",
                [
                    ["sensors", "--version"],
                ],
            ),
            version_command(
                "nvme_cli",
                [
                    ["nvme", "version"],
                ],
            ),
            version_command(
                "smartmontools",
                [
                    ["smartctl", "--version"],
                ],
            ),
            version_command(
                "stress_ng",
                [
                    ["stress-ng", "--version"],
                ],
            ),
        ]

        return {
            "tools": software,
            "available_count": sum(
                1
                for item in software
                if item["available"]
            ),
            "missing_count": sum(
                1
                for item in software
                if not item["available"]
            ),
        }

    def _scan_services(self) -> dict[str, Any]:
        service_names = [
            "docker",
            "postgresql",
            "ollama",
        ]

        results = []

        for service in service_names:
            active = run_command(
                [
                    "systemctl",
                    "is-active",
                    service,
                ]
            )

            enabled = run_command(
                [
                    "systemctl",
                    "is-enabled",
                    service,
                ]
            )

            results.append(
                {
                    "service": service,
                    "active": (
                        active.get("stdout")
                        == "active"
                    ),
                    "enabled": (
                        enabled.get("stdout")
                        == "enabled"
                    ),
                    "active_result": active,
                    "enabled_result": enabled,
                }
            )

        docker_info = run_json_command(
            [
                "docker",
                "info",
                "--format",
                "{{json .}}",
            ],
            timeout=30,
        )

        ollama_process = run_command(
            [
                "pgrep",
                "-a",
                "ollama",
            ]
        )

        postgres_process = run_command(
            [
                "pgrep",
                "-a",
                "postgres",
            ]
        )

        return {
            "services": results,
            "docker_info": docker_info,
            "ollama_process": ollama_process,
            "postgres_process": postgres_process,
            "service_start_attempted": False,
            "service_stop_attempted": False,
        }

    def _scan_virtualization(
        self,
    ) -> dict[str, Any]:
        systemd_detect = run_command(
            ["systemd-detect-virt"]
        )

        docker_containers = run_command(
            [
                "docker",
                "ps",
                "--format",
                "{{.ID}}\t{{.Names}}\t"
                "{{.Status}}\t{{.Image}}",
            ]
        )

        return {
            "systemd_detect_virt": systemd_detect,
            "virtualization_detected": (
                systemd_detect.get("status")
                == "success"
                and systemd_detect.get(
                    "stdout"
                )
                not in {
                    "",
                    "none",
                }
            ),
            "docker_containers": docker_containers,
        }

    def _scan_repository(
        self,
    ) -> dict[str, Any]:
        git_status = run_command(
            [
                "git",
                "status",
                "--short",
                "--branch",
            ]
        )

        git_branch = run_command(
            [
                "git",
                "branch",
                "--show-current",
            ]
        )

        git_commit = run_command(
            [
                "git",
                "rev-parse",
                "HEAD",
            ]
        )

        phase135_manifest = (
            self.repository_root
            / "runtime"
            / "audits"
            / "phase135_freeze_manifest_latest.json"
        )

        return {
            "git_status": git_status,
            "branch": git_branch.get(
                "stdout"
            ),
            "commit": git_commit.get(
                "stdout"
            ),
            "phase135_freeze_manifest_present": (
                phase135_manifest.is_file()
            ),
            "phase135_freeze_manifest_path": (
                str(phase135_manifest)
            ),
        }

    def _scan_resource_snapshot(
        self,
    ) -> dict[str, Any]:
        loadavg = self._read_text_file(
            Path("/proc/loadavg")
        )

        uptime = self._read_text_file(
            Path("/proc/uptime")
        )

        processes = run_command(
            [
                "ps",
                "-eo",
                "pid,comm,%cpu,%mem",
                "--sort=-%cpu",
            ]
        )

        top_processes = []

        if processes.get("stdout"):
            top_processes = (
                processes["stdout"]
                .splitlines()[:16]
            )

        return {
            "load_average": loadavg,
            "uptime_raw": uptime,
            "top_processes": top_processes,
            "snapshot_only": True,
        }

    def _build_summary(
        self,
        *,
        cpu: dict[str, Any],
        memory: dict[str, Any],
        gpu: dict[str, Any],
        storage: dict[str, Any],
        network: dict[str, Any],
        sensors: dict[str, Any],
        software: dict[str, Any],
        services: dict[str, Any],
    ) -> dict[str, Any]:
        service_map = {
            item["service"]: item["active"]
            for item in services.get(
                "services",
                [],
            )
        }

        root_storage_gib = sum(
            float(
                device.get(
                    "size_gib",
                    0,
                )
                or 0
            )
            for device in storage.get(
                "devices",
                [],
            )
        )

        return {
            "cpu_model": cpu.get(
                "model_name"
            ),
            "physical_cores": cpu.get(
                "physical_cores"
            ),
            "logical_cpus": cpu.get(
                "logical_cpus"
            ),
            "memory_gib": memory.get(
                "total_gib"
            ),
            "gpu_vendor": gpu.get(
                "detected_vendor"
            ),
            "storage_device_count": storage.get(
                "device_count"
            ),
            "total_discovered_storage_gib": round(
                root_storage_gib,
                2,
            ),
            "active_network_interfaces": network.get(
                "active_interfaces",
                [],
            ),
            "temperature_sensor_count": sensors.get(
                "temperature_count",
                0,
            ),
            "fan_sensor_count": sensors.get(
                "fan_sensor_count",
                0,
            ),
            "software_tools_available": software.get(
                "available_count",
                0,
            ),
            "software_tools_missing": software.get(
                "missing_count",
                0,
            ),
            "docker_active": service_map.get(
                "docker",
                False,
            ),
            "postgresql_active": service_map.get(
                "postgresql",
                False,
            ),
            "ollama_active": service_map.get(
                "ollama",
                False,
            ),
            "hardware_grade": "not_started",
            "capacity_projection": "not_started",
            "infrastructure_readiness": "not_started",
        }

    @staticmethod
    def _build_limitations(
        *,
        motherboard: dict[str, Any],
        sensors: dict[str, Any],
        storage: dict[str, Any],
    ) -> list[str]:
        limitations = [
            (
                "Stage 1 performs discovery only and does not "
                "measure sustained throughput."
            ),
            (
                "No CPU, GPU, storage, database, network, or "
                "application benchmark was executed."
            ),
            (
                "No user-capacity estimate is produced until "
                "later Phase 136 stages."
            ),
        ]

        if not motherboard.get(
            "privileged_details_available",
            False,
        ):
            limitations.append(
                "Some motherboard, BIOS, and DIMM details "
                "were unavailable without passwordless root access."
            )

        if not sensors.get(
            "available",
            False,
        ):
            limitations.append(
                "Hardware temperature sensors were unavailable."
            )

        if storage.get(
            "nvme_list",
            {},
        ).get("status") != "success":
            limitations.append(
                "NVMe controller details were not fully available."
            )

        return limitations

    @staticmethod
    def _parse_key_value_file(
        path: Path,
        *,
        separator: str,
    ) -> dict[str, str]:
        results = {}

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            return results

        for line in text.splitlines():
            if separator not in line:
                continue

            key, value = line.split(
                separator,
                1,
            )

            results[
                key.strip().strip('"')
            ] = value.strip().strip('"')

        return results

    @staticmethod
    def _read_text_file(
        path: Path,
    ) -> str | None:
        try:
            return path.read_text(
                encoding="utf-8",
                errors="replace",
            ).strip()
        except OSError:
            return None

    @staticmethod
    def _int_value(
        value: Any,
    ) -> int | None:
        if value is None:
            return None

        match = re.search(
            r"-?\d+",
            str(value).replace(",", ""),
        )

        if not match:
            return None

        try:
            return int(match.group(0))
        except ValueError:
            return None

    @staticmethod
    def _float_value(
        value: Any,
    ) -> float | None:
        if value is None:
            return None

        match = re.search(
            r"-?\d+(?:\.\d+)?",
            str(value).replace(",", ""),
        )

        if not match:
            return None

        try:
            return float(match.group(0))
        except ValueError:
            return None

    @staticmethod
    def _bytes_to_gib(
        value: Any,
    ) -> float | None:
        try:
            return round(
                float(value)
                / 1024
                / 1024
                / 1024,
                2,
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _meminfo_bytes(
        value: str | None,
    ) -> int:
        if not value:
            return 0

        match = re.search(
            r"(\d+)",
            value,
        )

        if not match:
            return 0

        return int(
            match.group(1)
        ) * 1024

    @staticmethod
    def _read_cpu_frequency() -> dict[str, Any]:
        values = []

        for path in Path(
            "/sys/devices/system/cpu"
        ).glob(
            "cpu[0-9]*/cpufreq/scaling_cur_freq"
        ):
            try:
                values.append(
                    int(
                        path.read_text().strip()
                    )
                )
            except (
                OSError,
                ValueError,
            ):
                continue

        if not values:
            return {
                "available": False,
                "minimum_mhz": None,
                "maximum_mhz": None,
                "average_mhz": None,
            }

        return {
            "available": True,
            "minimum_mhz": round(
                min(values) / 1000,
                2,
            ),
            "maximum_mhz": round(
                max(values) / 1000,
                2,
            ),
            "average_mhz": round(
                (
                    sum(values)
                    / len(values)
                    / 1000
                ),
                2,
            ),
        }

    @staticmethod
    def _read_cpu_governors() -> dict[str, Any]:
        governors = {}

        for path in Path(
            "/sys/devices/system/cpu"
        ).glob(
            "cpu[0-9]*/cpufreq/"
            "scaling_governor"
        ):
            cpu_name = path.parts[-3]

            try:
                governors[cpu_name] = (
                    path.read_text().strip()
                )
            except OSError:
                continue

        counts: dict[str, int] = {}

        for governor in governors.values():
            counts[governor] = (
                counts.get(governor, 0)
                + 1
            )

        return {
            "per_cpu": dict(
                sorted(governors.items())
            ),
            "counts": dict(
                sorted(counts.items())
            ),
        }

    @staticmethod
    def _read_cpu_vulnerabilities() -> dict[str, str]:
        results = {}

        directory = Path(
            "/sys/devices/system/cpu/vulnerabilities"
        )

        if not directory.is_dir():
            return results

        for path in sorted(
            directory.iterdir()
        ):
            if not path.is_file():
                continue

            try:
                results[path.name] = (
                    path.read_text().strip()
                )
            except OSError:
                continue

        return results

    @staticmethod
    def _scan_amd_gpu_sysfs() -> dict[str, Any]:
        cards = []

        for card in sorted(
            Path("/sys/class/drm").glob(
                "card[0-9]*"
            )
        ):
            device = card / "device"

            vendor = (
                HardwarePlatformScanner
                ._read_text_file(
                    device / "vendor"
                )
            )

            if vendor != "0x1002":
                continue

            card_data = {
                "card": card.name,
                "vendor": vendor,
                "device": (
                    HardwarePlatformScanner
                    ._read_text_file(
                        device / "device"
                    )
                ),
                "driver": None,
                "vram_total_bytes": None,
                "vram_used_bytes": None,
            }

            driver_link = device / "driver"

            try:
                card_data["driver"] = (
                    driver_link.resolve().name
                )
            except OSError:
                pass

            for key, filename in {
                "vram_total_bytes": (
                    "mem_info_vram_total"
                ),
                "vram_used_bytes": (
                    "mem_info_vram_used"
                ),
            }.items():
                value = (
                    HardwarePlatformScanner
                    ._read_text_file(
                        device / filename
                    )
                )

                try:
                    card_data[key] = int(
                        value
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    pass

            if card_data[
                "vram_total_bytes"
            ] is not None:
                card_data["vram_total_gib"] = (
                    HardwarePlatformScanner
                    ._bytes_to_gib(
                        card_data[
                            "vram_total_bytes"
                        ]
                    )
                )

            cards.append(card_data)

        return {
            "detected": bool(cards),
            "cards": cards,
        }

    @staticmethod
    def _detect_gpu_vendor(
        blocks: list[str],
    ) -> str | None:
        joined = "\n".join(
            blocks
        ).lower()

        if (
            "amd" in joined
            or "advanced micro devices"
            in joined
            or "ati" in joined
        ):
            return "AMD"

        if "nvidia" in joined:
            return "NVIDIA"

        if "intel" in joined:
            return "Intel"

        return None

    @staticmethod
    def _extract_temperatures(
        payload: Any,
    ) -> list[dict[str, Any]]:
        results = []

        def walk(
            value: Any,
            path: list[str],
        ) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = path + [
                        str(key)
                    ]

                    if (
                        isinstance(
                            child,
                            (int, float),
                        )
                        and str(key).endswith(
                            "_input"
                        )
                        and (
                            "temp" in str(key).lower()
                            or any(
                                marker in " ".join(
                                    child_path
                                ).lower()
                                for marker in {
                                    "edge",
                                    "junction",
                                    "composite",
                                    "tctl",
                                    "tccd",
                                    "mem",
                                }
                            )
                        )
                    ):
                        results.append(
                            {
                                "sensor": ".".join(
                                    child_path
                                ),
                                "celsius": float(
                                    child
                                ),
                            }
                        )

                    walk(
                        child,
                        child_path,
                    )

            elif isinstance(value, list):
                for index, child in enumerate(
                    value
                ):
                    walk(
                        child,
                        path + [
                            str(index)
                        ],
                    )

        walk(
            payload,
            [],
        )

        return sorted(
            results,
            key=lambda item: item[
                "sensor"
            ],
        )

    @staticmethod
    def _extract_fan_speeds(
        payload: Any,
    ) -> list[dict[str, Any]]:
        results = []

        def walk(
            value: Any,
            path: list[str],
        ) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = path + [
                        str(key)
                    ]

                    if (
                        isinstance(
                            child,
                            (int, float),
                        )
                        and str(key).startswith(
                            "fan"
                        )
                        and str(key).endswith(
                            "_input"
                        )
                    ):
                        results.append(
                            {
                                "sensor": ".".join(
                                    child_path
                                ),
                                "rpm": float(child),
                            }
                        )

                    walk(
                        child,
                        child_path,
                    )

            elif isinstance(value, list):
                for index, child in enumerate(
                    value
                ):
                    walk(
                        child,
                        path + [
                            str(index)
                        ],
                    )

        walk(
            payload,
            [],
        )

        return sorted(
            results,
            key=lambda item: item[
                "sensor"
            ],
        )
