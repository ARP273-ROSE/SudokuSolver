![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

# SudokuSolver

**A bilingual (French/English) Sudoku solver, generator and tutor — solves any puzzle, generates new ones by difficulty, and teaches you the techniques to crack them yourself.**

---

## Features

### Core solver
- Bitmask-based constraint propagation
- Backtracking with Minimum Remaining Values (MRV) heuristic
- Solves the hardest published puzzles in milliseconds
- Unique-solution verification

### Human-style hint engine
Step-by-step solving with bilingual explanations for every move, using the techniques a human would apply:

- **Naked Single** — one candidate left in a cell
- **Hidden Single** — one cell left in a unit for a digit
- **Naked Pair / Triple** — exclusive candidate subsets
- **Hidden Pair** — hidden exclusive digit subsets
- **Pointing Pair / Triple** — box candidates aligned on a line
- **Box / Line Reduction** — line candidates confined to one box
- **X-Wing** — rectangular elimination pattern

### Puzzle generator
Four difficulty levels, each calibrated by clue count *and* by the hardest technique required to solve it:

| Level  | Clues | Max technique           |
|--------|-------|-------------------------|
| Easy   | 36–45 | Hidden Single           |
| Medium | 30–35 | Hidden Pair             |
| Hard   | 26–32 | Box / Line Reduction    |
| Expert | 22–28 | X-Wing                  |

Puzzles are generated with rotational symmetry and guaranteed unique solutions.

### GUI (PyQt6)
- Interactive 9×9 grid with keyboard and mouse input
- Candidate (pencil-mark) display with toggle
- Row / column / box / same-value highlighting on selection
- Visual hint overlay: pattern cells in green, eliminations in red
- Mistake checker against the generated solution
- Bilingual FR/EN (auto-detected from system locale, switchable at runtime)
- Every widget has a bilingual tooltip

### Robustness
- Generator and solver run in background threads — the UI never freezes
- Worker lifecycle handled defensively (no dangling Qt references, no "wrapped C++ object deleted" errors on repeated clicks)
- Uncaught exceptions write anonymised JSON crash reports (usernames and home paths stripped)
- Solver capped at 2 million search nodes to guarantee bounded worst-case effort

### Built-in learning guide
The **Help → Solving techniques** menu opens a full bilingual catalogue explaining each technique with examples. A standalone **`guide_techniques.pdf`** and **`manuel.pdf`** (user manual) are shipped alongside the source.

---

## Installation

### Windows
```
launch.bat
```
Creates a local virtual environment in `%APPDATA%\SudokuSolver\venv`, installs dependencies on first run, and launches the app silently.

### Linux / macOS
```bash
chmod +x launch.sh
./launch.sh
```
Creates a local virtual environment in `$XDG_DATA_HOME/SudokuSolver/venv`.

### Manual
```bash
python -m venv venv
venv/Scripts/activate      # Windows
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
python main.py
```

---

## Usage

- **Click** a cell (or use arrow keys) and type **1–9** to fill, **0 / Delete / Backspace** to clear.
- Pick a difficulty and click **New puzzle** to generate one.
- Stuck? Click **Hint** to see the next logical step highlighted and explained, or **Next step** to apply it automatically.
- **Check** compares your current entries against the solution and highlights mistakes in red.
- **Solve** fills in the complete solution instantly.

---

## Project layout

```
SudokuSolver/
├── main.py               # Entry point
├── i18n.py               # FR/EN translation layer
├── generate_logo.py      # Logo generator (Pillow)
├── sudoku/
│   ├── board.py          # Grid + candidate bitmasks
│   ├── solver.py         # Fast backtracking solver
│   ├── techniques.py     # Human-style techniques
│   └── generator.py      # Difficulty-rated puzzle generator
├── gui/
│   ├── main_window.py    # Main window + menus
│   ├── grid_widget.py    # Interactive 9×9 grid
│   └── help_dialog.py    # How-to-play + techniques guide
├── launch.bat / launch.sh
├── requirements.txt
└── VERSION
```

---

## License

MIT
