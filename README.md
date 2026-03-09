# Usage guide
> [!NOTE]
> This script is meant for RM6785. It will work on other device
> but you will need to update the node paths.

1. Make sure you have `tsu` and `python` installed in Termux. If
   not, run this:
```bash
pkg install tsu python
```

2. Install the script via PyPI:
```bash
pip3 install -U battery-monitor
```

3. Run the script:
```bash
sudo battery
```

On step 3, it will prompt you to enter the device's battery capacity.
For example, realme 6's battery capacity is 4300 mAh, so enter 4300
without the mAh.

