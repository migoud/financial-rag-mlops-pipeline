import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import json

class ParseAndCleanElement(beam.DoFn):
    def process(self, element):
        try:
            raw_string = element.decode('utf-8')
            data = json.loads(raw_string)
            
            # Map values out carefully to prevent missing keys
            t_id = data.get('event_id') or data.get('transaction_id') or "unknown"
            u_id = data.get('user_id') or "usr-michaela-test"
            idx_val = float(data.get('index_value', 0.0))
            ts = data.get('timestamp')
            
            # Contextual summaries keeping your publisher metrics safe
            prompt_str = f"Real-time tracking for {data.get('category', 'General Metrics')}"
            context_str = f"City location tracking data: {data.get('city', 'Unknown')}"
            
            # STRICT FILTERING: Build a clean dictionary matching ONLY your BigQuery table columns
            final_record = {
                "transaction_id": str(t_id),
                "user_id": str(u_id),
                "prompt": str(prompt_str),
                "context": str(context_str),
                "index_value": idx_val,
                "timestamp": ts if ts else None
            }
            
            if 0.0 < idx_val < 500.0:
                yield final_record
        except Exception as e:
            pass

def run():
    options = PipelineOptions(
        streaming=True,
        project="project-2e0885aa-8f3e-4da5-86a",
        region="us-central1"
    )

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(
                subscription="projects/project-2e0885aa-8f3e-4da5-86a/subscriptions/cost-of-living-sub"
            )
            | "CleanAndParse" >> beam.ParDo(ParseAndCleanElement())
            
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                table="project-2e0885aa-8f3e-4da5-86a:realtime_metrics.raw_transactions",
                schema="transaction_id:STRING, user_id:STRING, prompt:STRING, context:STRING, index_value:FLOAT, timestamp:TIMESTAMP",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                additional_bq_parameters={"tableReference":{"location": "us-central1"}}
            )
        )

if __name__ == '__main__':
    run()
