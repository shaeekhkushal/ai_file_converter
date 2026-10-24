import warnings

from main import main


if __name__ == "__main__":
    warnings.warn(
        "gui_tkinter.py is deprecated; launch the PyQt desktop app with `python main.py`.",
        FutureWarning,
        stacklevel=2,
    )
    raise SystemExit(main())
