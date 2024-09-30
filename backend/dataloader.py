"""CLI entrypoint for staged ingestion pipeline."""

from pipeline.orchestrator import run_ingestion


def main():
    run_ingestion()


if __name__ == "__main__":
    main()
