"""scitex-logging quickstart: structured logging + custom warning types."""

import warnings

import scitex_logging


def main():
    # 1. getLogger — module-style logger like stdlib logging.
    log = scitex_logging.getLogger("quickstart")
    log.info("hello from scitex-logging")

    # 2. Level constants are exported.
    print(
        "DEBUG/INFO/SUCCESS:",
        scitex_logging.DEBUG,
        scitex_logging.INFO,
        scitex_logging.SUCCESS,
    )

    # 3. set_level / get_level round-trip.
    scitex_logging.set_level("DEBUG")
    print("level:", scitex_logging.get_level())

    # 4. SciTeX-specific exceptions are usable as regular exceptions.
    try:
        raise scitex_logging.PathNotFoundError("/no/such/path")
    except scitex_logging.SciTeXError as exc:
        print("caught SciTeXError:", type(exc).__name__, str(exc))

    # 5. Custom warnings categories work with warnings.warn.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warnings.warn("deprecated thing", scitex_logging.SciTeXDeprecationWarning)
        assert any(
            issubclass(w.category, scitex_logging.SciTeXDeprecationWarning)
            for w in caught
        )
        print("deprecation warning emitted")


if __name__ == "__main__":
    main()
