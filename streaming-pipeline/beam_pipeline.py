import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows
from apache_beam.transforms.deduplicate import Deduplicate
import json

class ParseAndCleanElement(beam.DoFn):
    def process(self, element):
        try:
            data = json.loads(element.decode('utf-8'))
            if 0.0 < data.get('index_value', 0.0) < 500.0:
                yield data
        except Exception as e:
            pass 

def run():
    options = PipelineOptions(
        streaming=True,
        project="project-2e0885aa-8f3e-4da5-86a",
        region="us-central1",
        temp_location="gs://project-2e0885aa-8f3e-4da5-86a-dataflow/temp"
    )

    with beam.Pipeline(options=options) as p:
        (
            p
            # 1. Read from your active subscription
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(
                subscription="projects/project-2e0885aa-8f3e-4da5-86a/subscriptions/cost-of-living-sub"
            )
            | "CleanAndParse" >> beam.ParDo(ParseAndCleanElement())
            
            # 2. Enforce stateful deduplication over a 10-minute processing window
            | "KeyByTransactionId" >> beam.Map(lambda x: (x.get('transaction_id', 'unknown'), x))
            | "DeduplicateRecords" >> Deduplicate(processing_time_duration=600)
            | "DropKeys" >> beam.Values()
            
            # 3. Group streaming telemetry into 10-second fixed windows for immediate local validation
            | "ApplyFixedWindows" >> beam.WindowInto(FixedWindows(10))
            
            # 4. Stream the finalized records directly into BigQuery
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
