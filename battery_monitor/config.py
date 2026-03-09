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

import atexit
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import tomlkit
import tomlkit.container


@dataclass
class NodePaths:
    current: str = "/sys/class/power_supply/battery/current"
    voltage: str = "/sys/class/power_supply/battery/voltage_now"
    voltage_usb: str = "/sys/class/power_supply/usb/device/ADC_Charger_Voltage"
    capacity: str = "/sys/class/power_supply/battery/capacity"
    status: str = "/sys/class/power_supply/battery/status"
    temp: str = "/sys/class/power_supply/battery/temp"
    voocchg_ing: str = "/sys/class/power_supply/battery/voocchg_ing"
    fastcharger: str = "/sys/class/power_supply/battery/fastcharger"
    batt_fcc: str = "/sys/class/power_supply/battery/batt_fcc"
    cool_down: str = "/sys/class/power_supply/battery/voocchg_ing"


@dataclass
class ConfigDefaults:
    design_capacity: int = 4300
    enable_vooc: bool = True
    voltage_unit_battery: str = "auto"
    voltage_unit_usb: str = "auto"
    nodepath: NodePaths = field(default_factory=NodePaths)


class Config:
    DEFAULTS = ConfigDefaults()

    def __init__(self, file: Path):
        self.file = file

        if file.exists():
            with file.open("r") as f:
                self.tomlcfg: tomlkit.TOMLDocument = tomlkit.load(f)
        else:
            self.tomlcfg = tomlkit.TOMLDocument()

        atexit.register(self.pre_exit)

    def pre_exit(self) -> None:
        with self.file.open("w") as f:
            tomlkit.dump(self.tomlcfg, f)

    def _get(self, key: str) -> Any:
        if "." in key:
            table, subkey = key.split(".", 1)
            toml_table = self.tomlcfg.get(table)
            if toml_table and subkey in toml_table:
                return toml_table[subkey]
            self._set(key, getattr(getattr(self.DEFAULTS, table), subkey))
            return self._get(key)
        if key in self.tomlcfg:
            return self.tomlcfg[key]
        if key == "design_capacity":
            value = input("Enter your device's design battery capacity: ")
            try:
                self._set(key, int(value))
            except ValueError as e:
                e.add_note("not a valid number!")
                raise
        else:
            self._set(key, getattr(self.DEFAULTS, key))
        return self._get(key)

    def _set(self, key: str, value: Any) -> None:
        if "." in key:
            table, subkey = key.split(".", 1)
            if table not in self.tomlcfg:
                self.tomlcfg[table] = tomlkit.table()
            cast(tomlkit.container.Table, self.tomlcfg[table])[subkey] = value
        else:
            self.tomlcfg[key] = value

    @property
    def design_capacity(self) -> int:
        return self._get("design_capacity")

    @design_capacity.setter
    def design_capacity(self, value: int) -> None:
        self._set("design_capacity", value)

    @property
    def enable_vooc(self) -> bool:
        return self._get("enable_vooc")

    @enable_vooc.setter
    def enable_vooc(self, value: bool) -> None:
        self._set("enable_vooc", value)

    @property
    def voltage_unit_battery(self) -> str:
        return self._get("voltage_unit_battery")

    @voltage_unit_battery.setter
    def voltage_unit_battery(self, value: str) -> None:
        self._set("voltage_unit_battery", value)

    @property
    def voltage_unit_usb(self) -> str:
        return self._get("voltage_unit_usb")

    @voltage_unit_usb.setter
    def voltage_unit_usb(self, value: str) -> None:
        self._set("voltage_unit_usb", value)

    @property
    def nodepath_current(self) -> str:
        return self._get("nodepath.current")

    @nodepath_current.setter
    def nodepath_current(self, value: str) -> None:
        self._set("nodepath.current", value)

    @property
    def nodepath_voltage(self) -> str:
        return self._get("nodepath.voltage")

    @nodepath_voltage.setter
    def nodepath_voltage(self, value: str) -> None:
        self._set("nodepath.voltage", value)

    @property
    def nodepath_voltage_usb(self) -> str:
        return self._get("nodepath.voltage_usb")

    @nodepath_voltage_usb.setter
    def nodepath_voltage_usb(self, value: str) -> None:
        self._set("nodepath.voltage_usb", value)

    @property
    def nodepath_capacity(self) -> str:
        return self._get("nodepath.capacity")

    @nodepath_capacity.setter
    def nodepath_capacity(self, value: str) -> None:
        self._set("nodepath.capacity", value)

    @property
    def nodepath_status(self) -> str:
        return self._get("nodepath.status")

    @nodepath_status.setter
    def nodepath_status(self, value: str) -> None:
        self._set("nodepath.status", value)

    @property
    def nodepath_temp(self) -> str:
        return self._get("nodepath.temp")

    @nodepath_temp.setter
    def nodepath_temp(self, value: str) -> None:
        self._set("nodepath.temp", value)

    @property
    def nodepath_voocchg_ing(self) -> str:
        return self._get("nodepath.voocchg_ing")

    @nodepath_voocchg_ing.setter
    def nodepath_voocchg_ing(self, value: str) -> None:
        self._set("nodepath.voocchg_ing", value)

    @property
    def nodepath_fastcharger(self) -> str:
        return self._get("nodepath.fastcharger")

    @nodepath_fastcharger.setter
    def nodepath_fastcharger(self, value: str) -> None:
        self._set("nodepath.fastcharger", value)

    @property
    def nodepath_batt_fcc(self) -> str:
        return self._get("nodepath.batt_fcc")

    @nodepath_batt_fcc.setter
    def nodepath_batt_fcc(self, value: str) -> None:
        self._set("nodepath.batt_fcc", value)

    @property
    def nodepath_cool_down(self) -> str:
        return self._get("nodepath.cool_down")

    @nodepath_cool_down.setter
    def nodepath_cool_down(self, value: str) -> None:
        self._set("nodepath.cool_down", value)
