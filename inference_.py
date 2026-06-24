import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import streamlit as st
import warnings


warnings.filterwarnings("ignore")

# ================================
# CONFIG
# ================================
CLASSIFIER_PATH = "./qwen_phishing_classifier"
BASE_MODEL_PATH = "Qwen/Qwen2.5-3B-Instruct"

# ================================
# MODEL LOADER (CACHED)
# ================================
@st.cache_resource
def load_models():
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    quantization_config=quant_config,
    device_map="auto",
    trust_remote_code=True,
)

    clf_model = PeftModel.from_pretrained(
        base_model,
        CLASSIFIER_PATH,
        is_trainable=False
    )

    clf_tokenizer = AutoTokenizer.from_pretrained(CLASSIFIER_PATH)
    exp_tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)

    return clf_model, clf_tokenizer, base_model, exp_tokenizer

# ================================
# CORE FUNCTION
# ================================
def detect_and_explain(subject: str):
    if not subject or subject.strip() == "":
        return "EMPTY", "Please enter a subject line.",0

    clf_model, clf_tokenizer, exp_model, exp_tokenizer = load_models()

    # ---------- CLASSIFIER ----------
    clf_prompt = f"""<|im_start|>system
You are a precise phishing email subject classifier. Reply with ONLY one word: PHISHING or LEGITIMATE.
<|im_start|>user
Analyze this email subject:

Subject: {subject}
<|im_start|>assistant
"""

    inputs = clf_tokenizer(clf_prompt, return_tensors="pt").to(clf_model.device)

    with torch.no_grad():

        # Get prediction probabilities
        logits_output = clf_model(**inputs)

        logits = logits_output.logits[:, -1, :]
        probs = torch.softmax(logits, dim=-1)

        # Highest confidence value
        confidence = torch.max(probs).item()

        # Convert to percentage
        risk_score = round(confidence * 100, 2)

        # Generate verdict
        outputs = clf_model.generate(
            **inputs,
            max_new_tokens=20,
            temperature=0.0,
            do_sample=False,
            eos_token_id=clf_tokenizer.eos_token_id,
            pad_token_id=clf_tokenizer.pad_token_id or clf_tokenizer.eos_token_id,
        )

    generated = outputs[0][inputs.input_ids.shape[1]:]
    verdict_text = clf_tokenizer.decode(generated, skip_special_tokens=True).upper()

    if "PHISHING" in verdict_text:
        verdict = "PHISHING"
    elif "LEGIT" in verdict_text:
        verdict = "LEGITIMATE"
    else:
        verdict = "UNKNOWN"

    # ---------- EXPLAINER ----------
    prompt = f'''You are an expert phishing analyst. Limit the words only for 100.
Analyze the email subject line and the given verdict. .

few_shot_examples = [
    {{
        "subject": "Urgent: Verify your account immediately or it will be suspended!!!",
        "verdict": "PHISHING",
        "explanation": """The subject uses strong urgency tactics with words like "Urgent" and "immediately" to pressure the recipient into quick action. It also includes a clear threat of account suspension, which is a common fear-based technique in phishing. The excessive exclamation marks (!!!) make the tone unprofessional and alarming. Additionally, the generic "your account" phrasing without any specific details is typical of mass phishing campaigns.

Final Verdict: This is very likely a phishing attempt and should be treated with high caution."""
    }},
    {{
        "subject": "Weekly team meeting notes - April 17",
        "verdict": "LEGITIMATE",
        "explanation": """The subject has a calm and routine tone with no urgency or pressure to act immediately. There are no threats or fear-inducing words present. The wording is clean, professional, and specific to an internal team activity. The structure is straightforward and lacks any suspicious punctuation or dramatic language.

Final Verdict: This appears to be a legitimate business communication."""
    }},
    {{
        "subject": "Your account has been compromised - Take action now to secure it",
        "verdict": "PHISHING",
        "explanation": """This subject creates immediate panic by claiming the account is compromised. It combines urgency ("Take action now") with a serious threat to push the user into clicking without thinking. The phrasing is generic and impersonal. The overall tone is alarming and inconsistent with how legitimate companies usually communicate security issues.

Final Verdict: This is a classic phishing attempt designed to exploit fear."""
    }},
    {{
        "subject": "Invoice #478292 - Payment overdue - Please review",
        "verdict": "LEGITIMATE",
        "explanation": """The subject is specific with an invoice number and sounds like a standard financial reminder. There is mild urgency but no extreme pressure or threats. The language is professional and factual. It does not contain suspicious formatting, excessive punctuation, or generic alarming phrases.

Final Verdict: This looks like a normal legitimate business email."""
    }}
]

Subject: {subject}
Verdict: {verdict}

Explanation:'''

    inputs_exp = exp_tokenizer(prompt, return_tensors="pt").to(exp_model.device)

    with torch.no_grad():
        out = exp_model.generate(
            **inputs_exp,
            max_new_tokens=200,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

    explanation = exp_tokenizer.decode(out[0], skip_special_tokens=True)

    if "Explanation:" in explanation:
        explanation = explanation.split("Explanation:")[-1].strip()

    return verdict, explanation, risk_score