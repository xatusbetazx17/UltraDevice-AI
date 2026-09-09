# Contributing

Create a feature branch from the reference branch. Install with
`python -m pip install -e '.[dev,plot]'`, then run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src firmware
python -m build
python scripts/firmware_manifest.py --check
```

Keep protocol changes versioned and test host/firmware compatibility. Add regression
tests for changed energy accounting, limits or fault behavior. Preserve the original
MIT notices. Update the capability matrix when behavior changes and clearly label
hardware-unverified code. Include measured acceptance records for hardware claims.
