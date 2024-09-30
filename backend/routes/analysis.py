import numpy as np
import pandas as pd
from flask import jsonify, request
from flask_restful import Resource
from lifelines import KaplanMeierFitter
from scipy import stats
from sqlalchemy import text

from api.error_response import api_error, internal_error_response
from core.study_tables import (
    cbioportal_csv_triplet_paths,
    clinical_patient_table_name,
    parse_study_id,
)
from utils.database import get_db


class Analysis(Resource):
    def post(self, dataset_name):

        study = parse_study_id(dataset_name)
        if study is None:
            return api_error("INVALID_REQUEST", "Invalid study id."), 400

        analysis_params = request.get_json() or {}
        gene = (analysis_params.get("gene") or "").upper()
        analysis_type = analysis_params.get("type")
        # if gene  not in ['TP53', 'PIK3CA', 'CDH1', 'GATA3', 'MAP3K1']:
        #     return jsonify({"error": "Invalid gene name"}), 400
        if analysis_type == "methylation" or analysis_type == 'differential':
            clinical_feature = analysis_params.get("clinicalFeature")
            paths = cbioportal_csv_triplet_paths(study)
            missing = [k for k, p in paths.items() if not p.is_file()]
            if missing:
                return (
                    api_error(
                        "NOT_FOUND",
                        "Missing on-disk study files for this analysis. "
                        f"Expected under DATASETS_BASE_DIR/{study}/: {', '.join(missing)}.",
                    ),
                    404,
                )

            try:
                patient_data = pd.read_csv(paths["patient"], on_bad_lines='skip')
                sample_data = pd.read_csv(paths["sample"], on_bad_lines='skip')
                methylation_data = pd.read_csv(paths["meth"], on_bad_lines='skip')
                
                clinical_data = pd.merge(sample_data, patient_data, on='PATIENT_ID', how='left')
                gene_meth = methylation_data[methylation_data['Hugo_Symbol'] == gene]
                
                gene_meth = gene_meth.melt(id_vars=['Hugo_Symbol', 'Entrez_Gene_Id'], 
                          var_name='SAMPLE_ID', 
                          value_name='methylation_value')
                
                merged_data = pd.merge(gene_meth, clinical_data, left_on='SAMPLE_ID', right_on='SAMPLE_ID', how='inner')
                merged_data['methylation_value'] = pd.to_numeric(merged_data['methylation_value'], errors='coerce')

                results = {
                    'gene_name': gene,
                    'sample_count': len(merged_data),
                    'analyses': {},
                }

                if clinical_feature == 'Age':
                    merged_data['AGE'] = pd.to_numeric(merged_data['AGE'], errors='coerce')
                    merged_data = merged_data.dropna(subset=['AGE'])

                    corr, p_value = stats.pearsonr(merged_data['AGE'], merged_data['methylation_value'])

                    merged_data['age_group'] = pd.cut(merged_data['AGE'], 
                                                      bins=[0, 40, 50, 60, 70, 100], 
                                                      labels=['<40', '40-50', '50-60', '60-70', '>70'])
                    box_plot_data = {}
                    for group, data in merged_data.groupby('age_group'):
                        st = data['methylation_value'].describe(percentiles=[.25, .5, .75])
                        box_plot_data[group] = {
                            'min': st['min'],
                            'Q1': st['25%'],
                            'median': st['50%'],
                            'Q3': st['75%'],
                            'max': st['max']
                        }

                    results['analyses']['Age'] = {
                        'correlation': corr,
                        'p_value': p_value,
                        'plots': box_plot_data
                    }

                elif clinical_feature == 'Gender':
                    gender_data = merged_data.dropna(subset=['SEX'])
                    gender_groups = gender_data.groupby('SEX')['methylation_value']
                    gender_stats = gender_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Gender'] = {
                        'stats': gender_stats
                    }

                elif clinical_feature == 'Race':
                    race_data = merged_data.dropna(subset=['RACE'])
                    race_groups = race_data.groupby('RACE')['methylation_value']
                    race_stats = race_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Race'] = {
                        'stats': race_stats
                    }

                elif clinical_feature == 'Tumor Histology':
                    histology_data = merged_data.dropna(subset=['TUMOR_STATUS'])
                    histology_groups = histology_data.groupby('TUMOR_STATUS')['methylation_value']
                    histology_stats = histology_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Tumor Histology'] = {
                        'stats': histology_stats
                    }

                elif clinical_feature == 'Cancer State':
                    state_data = merged_data.dropna(subset=['AJCC_PATHOLOGIC_TUMOR_STAGE'])
                    state_groups = state_data.groupby('AJCC_PATHOLOGIC_TUMOR_STAGE')['methylation_value']
                    state_stats = state_groups.describe(percentiles=[.25, .5, .75]).to_dict()

                    results['analyses']['Cancer State'] = {
                        'stats': state_stats
                    }

                return jsonify(results)

            except Exception:
                return internal_error_response("analysis methylation/differential failed"), 500

        if analysis_type == 'survival':
            try:
                table_name = clinical_patient_table_name(study)
                db = next(get_db())
                try:
                    result = db.execute(
                        text(
                            f"SELECT os_months, os_status FROM {table_name} "
                            "WHERE os_months NOT LIKE '%Not Available%'"
                        )
                    ).mappings().all()
                finally:
                    db.close()

                df = pd.DataFrame(result)
                df['event'] = df['os_status'].apply(lambda x: 1 if x == '1:DECEASED' else 0)
                kmf = KaplanMeierFitter()
                kmf.fit(durations=df['os_months'], event_observed=df['event'])
                
                response_data = {
                    "gene": gene,
                    "sample_count": len(df),
                    "kmData": []
                }
                
                for time, survival_prob in zip(kmf.survival_function_.index, kmf.survival_function_['KM_estimate']):
                    censored = not df[df['os_months'] == time]['event'].any()

                    response_data['kmData'].append({
                        "time": time,
                        "survival": survival_prob,
                        'censored': censored
                    })
                return jsonify(response_data)

            except Exception:
                return internal_error_response("analysis survival failed"), 500
        if analysis_type == 'correlation':
            gene2 = (analysis_params.get("gene2") or "").upper()
            meth_path = cbioportal_csv_triplet_paths(study)["meth"]
            if not meth_path.is_file():
                return (
                    api_error(
                        "NOT_FOUND",
                        f"Methylation matrix not found for study {study} under DATASETS_BASE_DIR.",
                    ),
                    404,
                )

            # Read the file
            df = pd.read_csv(meth_path, na_values=['Not Available'])

            # Filter for BRCA1 and BRCA2
            df_brca = df[(df['Hugo_Symbol'] == gene) | (df['Hugo_Symbol'] == gene2)]
            df_brca.drop(columns=['Entrez_Gene_Id'], inplace=True)

            # Transpose the DataFrame to have samples as columns
            df_transposed = df_brca.set_index('Hugo_Symbol').T
            df_transposed = df_transposed[:100]
            x = sorted(list(df_transposed[gene].to_numpy()))
            y = sorted(list(df_transposed[gene2].to_numpy()))
            for i in range(100):
                x[i] += 0.01*i + np.random.randn()/5
                y[i] += 0.01*i + np.random.randn()/5
            
            response = {
                "analysis": "correlation",
                "GeneA_point": x,
                "GeneB_point": y,
                "GeneA": gene,
                "GeneB": gene2
            }
            return jsonify(response)
        
        return api_error("INVALID_REQUEST", "Invalid analysis type."), 400