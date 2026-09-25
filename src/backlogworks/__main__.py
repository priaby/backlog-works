# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Process entrypoint: `python -m backlogworks`. Wiring only, no logic."""

from backlogworks.config import Config
from backlogworks.web.server import serve


def main() -> None:
    serve(Config.from_env())


if __name__ == "__main__":
    main()
