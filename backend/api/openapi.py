OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "BCancerPortal API",
        "version": "1.0.0",
        "description": "Flask REST API for breast cancer genomics platform.",
    },
    "servers": [
        {"url": "/api/v1"},
    ],
    "paths": {
        "/datasets": {
            "get": {
                "summary": "Dataset catalog grouped by cancer type",
                "parameters": [
                    {
                        "name": "full_catalog",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                        "description": "If 1/true, list all active studies; default lists only studies with ingested clinical patient data.",
                    }
                ],
                "responses": {
                    "200": {"description": "Grouped map of cancer type to dataset entries"},
                },
            }
        },
        "/datasets/{studyId}/data-status": {
            "get": {
                "summary": "Study data plane flags (ingested clinical + matrix file on disk)",
                "parameters": [
                    {
                        "name": "studyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {"description": "Status object returned"},
                    "400": {"description": "Invalid study id"},
                },
            }
        },
        "/analysis/jobs": {
            "post": {
                "summary": "Submit async analysis job",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AnalysisJobCreateRequest"
                            }
                        }
                    },
                },
                "responses": {
                    "202": {
                        "description": "Job accepted",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnalysisJobCreateResponse"
                                }
                            }
                        },
                    },
                    "400": {"description": "Validation error"},
                },
            }
        },
        "/analysis/jobs/{jobId}": {
            "get": {
                "summary": "Get async analysis job status",
                "parameters": [
                    {
                        "name": "jobId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Status returned",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnalysisJobStatusResponse"
                                }
                            }
                        },
                    },
                    "404": {"description": "Job not found"},
                },
            }
        },
        "/analysis/jobs/{jobId}/result": {
            "get": {
                "summary": "Get async analysis job result",
                "parameters": [
                    {
                        "name": "jobId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Completed result",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnalysisJobResultResponse"
                                }
                            }
                        },
                    },
                    "202": {"description": "Result not ready"},
                    "404": {"description": "Job not found"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "AnalysisJobCreateRequest": {
                "type": "object",
                "required": ["study_id"],
                "properties": {
                    "study_id": {"type": "string"},
                    "job_type": {
                        "type": "string",
                        "default": "generic",
                        "description": "Use llm_infer for OpenAI-compatible LLM calls (optional; stub if not configured).",
                    },
                    "parameters": {"type": "object"},
                },
            },
            "AnalysisJobCreateResponse": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "status": {"type": "string"},
                    "study_id": {"type": "string"},
                    "job_type": {"type": "string"},
                },
            },
            "AnalysisJobStatusResponse": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "status": {"type": "string"},
                    "study_id": {"type": "string"},
                    "job_type": {"type": "string"},
                    "queued_at": {"type": "string", "nullable": True},
                    "started_at": {"type": "string", "nullable": True},
                    "finished_at": {"type": "string", "nullable": True},
                    "error_message": {"type": "string", "nullable": True},
                },
            },
            "AnalysisJobResultResponse": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "result": {"type": "object"},
                },
            },
        }
    },
}

