# UltraDevice AI — prototipo de referencia

**Autor: Marcelo Collado · Licencia MIT**

Esta rama incluye un simulador instalable, una demostración que funciona sin hardware,
un controlador de modos, comunicación USB y firmware de referencia para Raspberry Pi
Pico/Pico H original (RP2040, sin Wi-Fi).

**No es un dispositivo comercial terminado.** El software está probado; el firmware
necesita pruebas en una placa real. La transformación física, el camuflaje óptico,
los materiales que se reparan solos y una fuente ilimitada de energía siguen siendo
ideas conceptuales.

## Probar sin comprar piezas

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
ultradevice demo --seconds 95 --out outputs/demo.jsonl
ultradevice check-log --input outputs/demo.jsonl
```

La demostración recorre 95 segundos virtuales inmediatamente. Los datos simulados
se identifican como `simulated`. No se envía información a Internet.

Para fabricar el prototipo básico, consulta la [lista de piezas y conexiones](hardware/README.md).
La placa mide temperatura y controla su LED. No incluye medidor de batería: los datos
no disponibles aparecen como `null`, sin inventar porcentajes de carga.

La [tabla de capacidades](docs/capabilities.md) distingue lo implementado de lo
pendiente. Las empresas pueden reutilizar el código según la [licencia MIT](LICENSE),
conservando sus avisos. Una prueba de software no sustituye la validación electrónica,
térmica, mecánica o de fabricación.
