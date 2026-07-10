# Financial RAG Pipeline (GCP / MLOps)

A production-grade, cost-optimized pipeline mapping macroeconomic cost-of-living data (US BLS + World Bank WDI) to serve grounded context through an LLM RAG agent. 

## 🛠️ Tech Stack
- **Compute & Orchestration:** GKE Autopilot, Docker, FastAPI, Cloud Build (CI/CD)
- **Data Infrastructure:** BigQuery Studio, Dataflow (Apache Beam), Cloud Pub/Sub, Dataform
- **AI/ML Engine:** Vertex AI Studio (Gemini 2.5 Flash), Vertex AI Vector Search, BigQuery ML

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
- [x] **Containerization & GKE Autopilot Runtime Orchestration**
  - Package the RAG backend into a Dockerized FastAPI application with standardized resource constraints.
  - Deploy the API runtime to GKE autopilot, integrating a Horizontal Pod Autoscaler (HPA) to manage scale and automatically reduce resource footprints during inactivity. 
- [x] **Message Ingestion & CI/CD Automation**
  - Architect and configure a Cloud Pub/Sub messaging layer to handle a simulated incoming data stream of real-time cost-of-living updates.
  - Configure automated testing and automated image compilation using continuous Cloud Build triggers linked directly to GitHub repository commits.

### Phase 3: Streaming, Transformation, & Governance (Target: 3rd week of July)
- [x] **Dataflow Pipelines & Warehouse Optimization**
  - Build a streaming Apache Beam (Dataflow) pipeline to handle deduplication and windowing for incoming Pub/Sub data.
  - Orchestrate internal SQL transformations using Dataform and apply schema-level BigQuery Policy Tags.

---
# Pipeline Verified

## Infrastructure & Troubleshooting Notes

### Cross-Service IAM Permissions
During deployment, ensure that the core Google Compute Engine default service account (`134570236275-compute@developer.gserviceaccount.com`) has explicit permissions enabled to prevent silent `ImagePullBackOff` or storage errors:
* **Storage Admin** (`roles/storage.admin`): Required for staging build source code tarballs.
* **Artifact Registry Repo Admin** (`roles/artifactregistry.repoAdmin`): Required for pushing and writing production container tags.

### Production Build Flow
Always offload container compilation to **Google Cloud Build** to ensure network byte integrity and avoid local Docker proxy/handshake rejections:
\`\`\`bash
gcloud builds submit --tag us-central1-docker.pkg.dev/project-2e0885aa-8f3e-4da5-86a/rag-backend-repo/rag-service:v1 .
\`\`\`
