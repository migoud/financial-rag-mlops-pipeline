# Financial RAG Pipeline (GCP / MLOps)

A production-grade, enterprise-secured MLOps pipeline that ingests macro-economic and real-time cost-of-living telemetry data via streaming infrastructure, optimizing data warehousing transformations to serve highly grounded context through a Gemini-powered Retrieval-Augmented Generation (RAG) agent.

---

## 👥 Executive Summary 

This repository demonstrates an end-to-end Machine Learning & Data Engineering Pipeline built entirely on Google Cloud Platform (GCP). It showcases the ability to architect scalable microservices, manage streaming analytical data workflows, implement strict data governance frameworks, and securely deploy containerized AI solutions within production clusters.

* **Core Competencies:** MLOps, Data Engineering, Infrastructure-as-Code, Enterprise Cloud Security.
* **Key Achievements:** * Designed an infinite, fault-tolerant data stream using Apache Beam (Dataflow) that eliminates duplicate records under network strain.
  * Containerized and deployed a microservice API to Google Kubernetes Engine (GKE) Autopilot utilizing Workload Identity Federation for a zero-trust security profile.
  * Orchestrated programmatic database modeling and data masking transformations using Dataform and BigQuery ML.

---

## 🛠️ Project Architecture & Directory Layout

The codebase is organized into isolated modular domains following a production-first engineering layout:

```text
├── app/
│   ├── __init__.py
│   ├── engine.py           # Vertex AI integration and RAG generation engine
│   └── main.py             # FastAPI backend implementation with structured logging
├── notebooks/
│   ├── 3_model_monitoring.ipynb
│   ├── 3_model_monitoring_adversarial.ipynb
│   └── 3_rag_orchestration_loop.ipynb
├── sql/
│   ├── 1_data_ingestion.sql   # BigQuery public data federation queries
│   └── 2_model_training.sql    # BigQuery ML training, tuning, and evaluation
├── streaming-pipeline/
│   ├── beam_pipeline.py    # Apache Beam windowed streaming deduplication
│   └── publisher.py        # Real-time Pub/Sub mockup telemetry generator
├── tests/
│   ├── __init__.py
│   └── test_main.py        # API routing and behavioral unit tests
├── Dockerfile              # Multi-stage container compilation manifest
├── cloudbuild.yaml         # CI/CD automation and container build config
├── deployment.yaml         # Kubernetes pod and HPA layout rules
└── requirements.txt        # Frozen dependency tree specifications
