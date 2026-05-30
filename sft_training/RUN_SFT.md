# How to use the OpenAI SFT API 

## Step 1: Combine the JSONL files
The SFT API requires all training examples to exist in one big JSONL file. We generated training examples one at a time, so each training data point existed in its own JSONL file. 

To combine them, run the `combine_jsonl.py` file
```
python combine_jsonl.py
```

The current Salvatore uses the training examples in `sft_training/training_data/v3/`. The combined JSONL file is `sft_training/training_data/training_sft_v3.jsonl`. This can be used directly to reproduce results.

## Step 2: Run SFT 
After combining the JSONL files, you can run the `sft.py` file to create an SFT job. Once it's created, you should be able to see it on the OpenAI SFT dashboard (https://platform.openai.com/finetune).

