import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from flask_restful import Resource

from api.error_response import api_error, internal_error_response
from core.study_tables import expression_matrix_path, parse_study_id


def _matrix_path(study_id: str) -> Path:
    return expression_matrix_path(study_id)


def _matrix_cache_key(study_id: str) -> tuple[str, int, int]:
    path = _matrix_path(study_id)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    st = path.stat()
    return (study_id, int(st.st_mtime_ns), int(st.st_size))


@lru_cache(maxsize=16)
def _load_expression_matrix(cache_key: tuple[str, int, int]) -> pd.DataFrame:
    study_id = cache_key[0]
    path = _matrix_path(study_id)
    df = pd.read_csv(path)
    df = df.iloc[:200, :200]
    df.set_index("Hugo_Symbol", inplace=True)
    if "Entrez_Gene_Id" in df.columns:
        df.drop(columns=["Entrez_Gene_Id"], inplace=True)
    df = df.apply(pd.to_numeric, errors="coerce")
    df.fillna(0, inplace=True)
    return df


def _build_heatmap_figure(df: pd.DataFrame) -> go.Figure:
    z_values = np.round(df.values, 2)
    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=df.columns.tolist(),
            y=df.index.tolist(),
            colorscale="RdBu_r",
            colorbar=dict(title="Expression Level"),
            hoverongaps=False,
            hovertemplate="Gene: %{y}<br>Sample: %{x}<br>Expression: %{z:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Gene Expression Heatmap",
        xaxis=dict(
            title="Samples",
            tickangle=45,
            showticklabels=True,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="Genes",
            showticklabels=True,
            tickfont=dict(size=10),
        ),
        width=1200,
        height=800,
        margin=dict(l=100, r=50, t=50, b=100),
    )
    return fig


class Heatmap(Resource):
    """Plotly heatmap from study-specific expression matrix (CSV under DATASETS_BASE_DIR)."""

    def get(self, dataset_name):
        study = parse_study_id(dataset_name)
        if study is None:
            return api_error("INVALID_REQUEST", "Invalid study id."), 400
        path = _matrix_path(study)
        if not path.is_file():
            return (
                api_error(
                    "NOT_FOUND",
                    "Expression matrix file not found for this study. "
                    "Place data under DATASETS_BASE_DIR/<study_id>/ or run ingestion.",
                ),
                404,
            )
        try:
            key = _matrix_cache_key(study)
            df = _load_expression_matrix(key)
            fig = _build_heatmap_figure(df)
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception:
            return internal_error_response(f"GET heatmap failed study={study}"), 500
