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

from asyncio import new_event_loop
from importlib.metadata import version
from pathlib import Path

from rich.console import Console

from battery_monitor.config import Config

__version__ = version("battery-monitor")

CONFIG_PATH = Path.home() / "battery_config.toml"
config = Config(CONFIG_PATH)
console = Console()
event_loop = new_event_loop()
