from openai import OpenAI
client = OpenAI()

# Upload training file
file = client.files.create(
    file=open("training_data/training_sft_v3.jsonl", "rb"),
    purpose="fine-tune"
)

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4.1-mini-2025-04-14",
    # method={
    #     "type": "supervised",
    #     "supervised": {
    #         "hyperparameters": {
    #             "n_epochs": 5
    #         }
    #     },
    # },
)

print(f"Job ID: {job.id}")
print(f"Status: {job.status}")
