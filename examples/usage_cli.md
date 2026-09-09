# CLI examples

From an installed package, run `ultradevice --help` for all commands. No hardware is
needed for these examples. Output paths may be plain filenames or nested folders.

```bash
ultradevice runtime --battery-wh 12 --avg-load-w 2.8 --solar-w 0.6 --kinetic-w 0.2
ultradevice boost --battery-wh 12 --burst-w 10 --burst-sec 60
ultradevice duty --battery-wh 12 --target-hours 8 --p-hi 6 --p-lo 1.2 --harvest-w 0.5
ultradevice optimize --battery-wh 12 --target-hours 8 --out outputs/optimized.json
ultradevice size-battery --target-hours 8 --avg-load-w 0.1 --harvest-w 0.01
ultradevice profile --out outputs/custom.json
ultradevice randomize --seed 42 --out outputs/random.json
ultradevice validate-scenario --scenario outputs/random.json
ultradevice simulate --scenario outputs/custom.json --out outputs/ideal.csv
ultradevice simulate-physics --scenario examples/scenarios/bench_reference.json --out outputs/physics.csv
ultradevice report --csv outputs/physics.csv --out outputs/report.md
ultradevice plot --csv outputs/physics.csv --out outputs/plot.png
ultradevice demo --seconds 95 --out outputs/demo.jsonl
ultradevice check-log --input outputs/demo.jsonl
ultradevice schema --kind scenario --out outputs/scenario.schema.json
```

For an actual Pico, follow `hardware/README.md` first. Use `--config examples/controller.json`
to choose host thresholds. `--target-hours` and `--battery-wh` together enable the
runtime predictor only when the adapter reports actual load/harvest/SoC readings.
