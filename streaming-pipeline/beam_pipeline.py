import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import json

class ParseAndCleanElement(beam.DoFn):
    def process(self, element):
        # Decode raw Pub/Sub binary packet back to operational JSON dictionary
        try:
            data = json.loads(element.decode('utf-8'))
            # Filter out extreme index validation out-of-bounds metrics
            if 0.0 < data.get('index_value', 0.0) < 500.0:
                yield data
        except Exception as e:
            pass # Gracefully skip bad telemetry records for now

def run():
    options = PipelineOptions(
        streaming=True,
        project="project-2e0885aa-8f3e-4da5-86a"
    )

    # Note: Using the DirectRunner locally for architecture staging
    with beam.Pipeline(options=options) as p:
        (
            p 
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription="projects/project-2e0885aa-8f3e-4da5-86a/subscriptions/cost-of-living-sub")
            | "CleanAndParse" >> beam.ParDo(ParseAndCleanElement())
            | "LogPipelineElements" >> beam.Map(lambda x: print(f"🎯 Beam Ingested Element: {x}"))
        )

if __name__ == '__main__':
    run()
