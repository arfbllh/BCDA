from pipeline.matrix_store import is_matrix_file


def test_gistic_genes_tables_are_not_treated_as_wide_matrices():
    assert is_matrix_file("/x/data_gistic_genes_amp.txt") is False
    assert is_matrix_file("/x/data_gistic_genes_del.txt") is False


def test_other_gistic_named_files_can_still_be_matrices():
    assert is_matrix_file("/x/all_thresholded_by_genes_gistic2.txt") is True
