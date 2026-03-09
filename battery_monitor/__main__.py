# SPDX-License-Identifier: GPL-3.0-only
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (c) 2026, Firdaus Hakimi <hakimifirdaus944@gmail.com>

import asyncio
import contextlib
import sys
from enum import StrEnum

from anyio import Path
from rich import box
from rich.columns import Columns
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from battery_monitor import __version__, config, console, event_loop
from battery_monitor.util import read_node_nofail


class Unit(StrEnum):
    millivolt = "mV"
    microvolt = "µV"


type VoltageUnit = Unit
type UsbVoltageUnit = Unit


async def get_stats() -> tuple[dict, VoltageUnit, UsbVoltageUnit]:
    stats_task = {
        "status": event_loop.create_task(read_node_nofail(Path(config.nodepath_status))),
        "capacity": event_loop.create_task(read_node_nofail(Path(config.nodepath_capacity))),
        "current_mA": event_loop.create_task(read_node_nofail(Path(config.nodepath_current))),
        "voltage": event_loop.create_task(read_node_nofail(Path(config.nodepath_voltage))),
        "usb_voltage": event_loop.create_task(read_node_nofail(Path(config.nodepath_voltage_usb))),
        "temp": event_loop.create_task(read_node_nofail(Path(config.nodepath_temp))),
        "cool_down": event_loop.create_task(read_node_nofail(Path(config.nodepath_cool_down))),
        "voocchg_ing": event_loop.create_task(read_node_nofail(Path(config.nodepath_voocchg_ing))),
        "fastcharger": event_loop.create_task(read_node_nofail(Path(config.nodepath_fastcharger))),
        "batt_fcc": event_loop.create_task(read_node_nofail(Path(config.nodepath_batt_fcc))),
    }

    await asyncio.wait(stats_task.values())

    stats = {}
    for k, v in stats_task.items():
        stats.update({k: v.result()})

    voltage = stats.get("voltage", 0)
    try:
        v = abs(int(voltage))
        voltage_unit = Unit.microvolt if v > 9999 else Unit.millivolt
        wattage = (v / 1_000_000 if v > 9999 else v / 1000) * (int(stats.get("current_mA", 0)) / 1000)
    except Exception:  # noqa: BLE001
        voltage_unit = Unit.microvolt
        wattage = "[could not calculate wattage]"

    usb_voltage = stats.get("usb_voltage", 0)
    try:
        usbv = abs(int(usb_voltage))
        usb_voltage_unit = Unit.microvolt if usbv > 9999 else Unit.millivolt
        usb_wattage = (usbv / 1_000_000 if usbv > 9999 else usbv / 1000) * (int(stats.get("current_mA", 0)) / 1000)
    except Exception:  # noqa: BLE001
        usb_voltage_unit = Unit.microvolt
        usb_wattage = "[could not calculate USB wattage]"

    stats.update({
        "voltage": voltage,
        "usb_voltage": usb_voltage,
        "wattage": wattage,
        "usb_wattage": usb_wattage,
    })

    return stats, voltage_unit, usb_voltage_unit


def make_table(stats: dict, voltage_unit: VoltageUnit, usb_voltage_unit: UsbVoltageUnit) -> Panel:
    general = Table(title="General Info", box=box.SIMPLE, show_header=False)
    general.add_column(style="cyan")
    general.add_column(style="green")

    general.add_row("status", stats["status"])
    general.add_row("capacity", f"{stats['capacity']}%")

    fcc = stats["batt_fcc"]
    try:
        fcc = int(fcc)
    except ValueError:
        fcc = 0
    design = config.design_capacity
    pct = fcc / design * 100
    general.add_row("Battery Health", f"{fcc}/{design} ({pct:.2f}%)")

    with contextlib.suppress(TypeError):
        general.add_row("temp", stats["temp"] / 10)
    general.add_row("cool_down", stats["cool_down"])

    charging = Table(title="Charging Info", box=box.SIMPLE, show_header=False)
    charging.add_column(style="cyan")
    charging.add_column(style="green")

    with contextlib.suppress(ValueError):
        charging.add_row("current", f"{stats['current_mA']} ({abs(int(stats['current_mA']))}mA)")
    charging.add_row("voltage", f"{stats['voltage']}{voltage_unit.value}")
    charging.add_row("USB voltage", f"{stats['usb_voltage']}{usb_voltage_unit.value}")
    charging.add_row("wattage", f"{stats['wattage']}W")
    charging.add_row("USB wattage", f"{stats['usb_wattage']}W")
    charging.add_row("voocchg_ing", stats["voocchg_ing"])
    charging.add_row("fastcharger", stats["fastcharger"])

    return Panel(Columns([general, charging], title=f"Battery Monitor (by Hakimi) v{__version__}"))


async def entry() -> None:
    stats = await get_stats()
    with Live(make_table(stats[0], stats[1], stats[2]), console=console, refresh_per_second=5) as live:
        try:
            while True:
                stats = await get_stats()
                live.update(make_table(stats[0], stats[1], stats[2]))
                await asyncio.sleep(0.2)
        except Exception:
            live.stop()
            console.print_exception()
            raise


def main() -> None:
    try:
        event_loop.run_until_complete(entry())
    except Exception:
        console.print_exception()
    except KeyboardInterrupt:
        pass
    finally:
        pending = asyncio.all_tasks(event_loop)
        for task in pending:
            task.cancel()
        if pending:
            event_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        event_loop.close()
        sys.exit(0)
