from pipeline.orchestrator import run_ingestion


def main():
    """CLI entrypoint for staged ingestion pipeline."""
    run_ingestion(dataset_index_path="./datasets/datasets.csv", datasets_base_dir="datasets")


if __name__ == "__main__":
    main()