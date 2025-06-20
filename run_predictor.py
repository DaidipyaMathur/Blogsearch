import json
from transformers import pipeline
import torch

# --- Configuration ---
# The input file with all your data (labeled and unlabeled)
INPUT_FILE = "ground_truth_for_labeling.jsonl" 

# The new output file where results with model predictions will be saved
OUTPUT_FILE = "new_classified.jsonl" 

# The path to your fine-tuned model. 
# IMPORTANT: Look inside this folder and find the checkpoint with the highest number
# (e.g., 'checkpoint-15', 'checkpoint-210', etc.).
MODEL_PATH = "./blog_classifier_model/checkpoint-345" # <-- CORRECTED: Using the highest checkpoint number from your last training run.

# --- Main Script ---
def run_batch_prediction():
    """
    Loads a fine-tuned model and runs it on every entry in a JSONL file,
    saving the original data along with the model's prediction.
    """
    print("--- Starting Batch Prediction Script ---")

    # --- 1. Load the fine-tuned classifier model ---
    try:
        # Check if a GPU is available and use it, otherwise use CPU
        device = 0 if torch.cuda.is_available() else -1
        print(f"Loading model from: {MODEL_PATH}")
        classifier = pipeline(
            "sentiment-analysis", # This is the generic task name for text classification
            model=MODEL_PATH, 
            tokenizer=MODEL_PATH,
            device=device # Use GPU if available for much faster processing
        )
        print("Model loaded successfully.")
    except Exception as e:
        print(f"\n[ERROR] Could not load the model from '{MODEL_PATH}'.")
        print("Please make sure the path is correct and points to a valid model checkpoint.")
        print(f"Details: {e}")
        return

    # --- 2. Process the input file ---
    all_records = []
    try:
        with open(INPUT_FILE, 'r') as f:
            for line in f:
                all_records.append(json.loads(line))
        print(f"Loaded {len(all_records)} records from '{INPUT_FILE}'.")
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: '{INPUT_FILE}'. Please make sure it exists.")
        return

    # --- 3. Run predictions and write to the new file ---
    print(f"\nRunning predictions and writing to '{OUTPUT_FILE}'...")
    with open(OUTPUT_FILE, 'w') as f_out:
        for i, record in enumerate(all_records):
            
            # This is the core logic: get the text from the record
            text_to_classify = record.get("text", "")

            # Ensure there is text to classify
            if text_to_classify:
                try:
                    # Run the prediction. We only use the first 512 tokens for efficiency.
                    prediction = classifier(text_to_classify, truncation=True, max_length=512)[0]
                    
                    # Add the model's output to the record
                    record["model_label"] = prediction['label']
                    record["model_score"] = round(prediction['score'], 4)

                except Exception as e:
                    print(f"  -> Could not process record {i+1}. Error: {e}")
                    record["model_label"] = "CLASSIFICATION_ERROR"
                    record["model_score"] = 0.0
            else:
                record["model_label"] = "NO_TEXT"
                record["model_score"] = 0.0
            
            # Write the updated record to the new file
            f_out.write(json.dumps(record) + '\n')

            # Print a progress update every 100 records
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(all_records)} records...")

    print(f"\n--- Batch Prediction Complete ---")
    print(f"All records have been processed and saved to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    run_batch_prediction()
