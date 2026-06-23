# Financial RAG Pipeline (GCP / MLOps)

A production-grade, cost-optimized pipeline mapping macroeconomic cost-of-living data (US BLS + World Bank WDI) to serve grounded context through an LLM RAG agent. 

## 🛠️ Tech Stack
- **Compute & Orchestration:** GKE Autopilot, Docker, FastAPI, Cloud Build (CI/CD)
- **Data Infrastructure:** BigQuery Studio, Dataflow (Apache Beam), Cloud Pub/Sub, Dataform
- **AI/ML Engine:** Vertex AI Studio (Gemini 1.5 Flash), Vertex AI Vector Search, BigQuery ML

---

## 📊 Project Milestones & Progress Tracker

### Phase 1: Core Analytics & Predictive Modeling (Target: End of June)
- [x] **Data Federation & Baseline Modeling**
  - Federated raw `bigquery-public-data.bls` and `world_bank_wdi` tables into a single economic feature view.
  - Trained a BigQuery ML linear regression model using Batch Gradient Descent and tuned $L1/L2$ regularization weights.
  - *Source Code:* `sql/1_data_ingestion.sql`
- [x] **Generative Engine & RAG Architecture**
  - Build the Retrieval-Augmented Generation (RAG) orchestration loop in Vertex AI Workbench using Gemini 1.5 Flash.
  - Implement Vertex AI Model Monitoring to evaluate grounding metrics and capture hallucination indicators.

### Phase 2: Microservices & Deployment Infrastructure (Target: Middle of July)
- [ ] **Containerization & CI/CD Pipelines**
  - Package the RAG backend into a Dockerized FastAPI application.
  - Configure automated testing and image building using Cloud Build triggered by repository commits.
- [ ] **Message Ingestion & Orchestrated Scale**
  - Set up Cloud Pub/Sub to handle a simulated stream of real-time cost-of-living updates.
  - Deploy the API runtime to GKE Autopilot, configuring nodes to automatically scale down during inactivity.

### Phase 3: Streaming, Transformation, & Governance (Target: 3rd week of July)
- [ ] **Dataflow Pipelines & Warehouse Optimization**
  - Build a streaming Apache Beam (Dataflow) pipeline to handle deduplication and windowing for incoming Pub/Sub data.
  - Orchestrate internal SQL transformations using Dataform and apply schema-level BigQuery Policy Tags.
  - Create a Looker Studio dashboard tracking pipeline operational health and model data drift.

---
# Pipeline Verified
