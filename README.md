# Phishguard-Subject-Analysis
AI-powered phishing email subject detection system using a fine-tuned Qwen2.5 LLM with risk scoring, explainable AI, and a Streamlit web interface.
## Features

- ✅ Fine-tuned Qwen2.5-3B-Instruct model for phishing detection
- ✅ LoRA-based parameter-efficient fine-tuning
- ✅ Confidence-based risk scoring
- ✅ Explainable AI outputs
- ✅ Streamlit web application
- ✅ Interactive user interface with example subjects
- ✅ Quantized inference for efficient deployment

---

## System Architecture

1. User enters an email subject line.
2. The fine-tuned Qwen model predicts whether the subject is phishing or legitimate.
3. A confidence score is calculated and converted into a risk score.
4. The system generates a human-readable explanation.
5. Results are displayed through a Streamlit interface.

---

## Technologies Used

- Python
- PyTorch
- Hugging Face Transformers
- PEFT (LoRA)
- BitsAndBytes
- Streamlit
- Qwen2.5-3B-Instruct

---

## Project Structure

```text
PhishGuard-Subject-Analysis/
│
├── preprocessing.ipynb          # Dataset preprocessing
├── finetuning.ipynb             # Model fine-tuning workflow
├── inference_.py                # Inference and risk scoring pipeline
├── phishing_detector_app.py     # Streamlit application
├── .csv files                   # Datasets
├── README.md
