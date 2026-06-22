import time
import logging
import google.generativeai as genai
from app.core.config import settings

# Setup logger for Celery to pick up
logger = logging.getLogger(__name__)

# Configure the API key if it's provided
if settings.GEMINI_API_KEY:
    logger.info("GEMINI_API_KEY is successfully loaded.")
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.error("CRITICAL: GEMINI_API_KEY is NOT loaded. Check docker-compose.yml and .env variables.")
    
# Valid categories per the requirements
VALID_CATEGORIES = [
    "Food", "Shopping", "Travel", "Transport", 
    "Utilities", "Entertainment", "Cash Withdrawal", "Other"
]

def categorize_transaction(merchant: str, amount: float, currency: str, date: str) -> tuple[str, str, bool]:
    """
    Calls the Gemini API to categorize a transaction.
    Returns: (category, raw_response, failed_flag)
    """
    if not settings.GEMINI_API_KEY:
        logger.error(f"Skipping classification for merchant {merchant}: API Key not configured")
        return "Other", "API Key not configured", True

    prompt = f"""
    You are a financial transaction categorization assistant.
    Categorize the following transaction into exactly ONE of the following categories:
    {', '.join(VALID_CATEGORIES)}
    
    Transaction Details:
    - Merchant: {merchant}
    - Amount: {amount} {currency}
    - Date: {date}
    
    Respond ONLY with the category name. Do not include any other text, markdown, or punctuation.
    """
    
    # We use a simple loop for the maximum of 3 retries
    max_retries = 3
    
    # Use gemini-1.5-flash as it is fast and suitable for simple text classification tasks
    try:
        model_name = 'gemini-3.5-flash'
        model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized model: {model_name} for transaction categorization")
    except Exception as e:
        logger.error(f"Error initializing Gemini model: {str(e)}", exc_info=True)
        return "Other", f"Error initializing model: {str(e)}", True
        
    for attempt in range(max_retries):
        try:
            logger.info(f"Gemini classification attempt {attempt + 1}/{max_retries} for merchant: {merchant}")
            logger.info(f"Prompt sent: {prompt.strip()}")
            
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            
            logger.info(f"Gemini raw response: {raw_text}")
            
            # Clean up the response just in case the model adds punctuation
            clean_text = raw_text.strip("'.\"* ")
            
            # Find the closest matching category
            # We do a case-insensitive match
            for valid_cat in VALID_CATEGORIES:
                if valid_cat.lower() == clean_text.lower():
                    logger.info(f"Successfully categorized as: {valid_cat}. Successful Gemini response: {raw_text}")
                    return valid_cat, raw_text, False
                    
            # If the model returned something unexpected, fallback to 'Other'
            logger.warning(f"Response '{raw_text}' did not match valid categories. Falling back to 'Other'.")
            return "Other", raw_text, False
            
        except Exception as e:
            # We log the full stack trace to the Celery logs
            logger.error(f"Gemini API request failed on attempt {attempt + 1}: {str(e)}", exc_info=True)
            
            # If it's the last attempt, return failure
            if attempt == max_retries - 1:
                return "Other", str(e), True
                
            # Otherwise, wait a second and try again
            time.sleep(1)
            
    # Fallback (should be unreachable due to loop logic)
    return "Other", "Unknown failure", True

def generate_summary_narrative(total_spend_inr: float, total_spend_usd: float, top_merchants: dict, anomaly_count: int) -> tuple[str, str]:
    """
    Calls Gemini API to generate a narrative and risk level based on the transaction aggregations.
    Returns: (risk_level, narrative)
    """
    if not settings.GEMINI_API_KEY:
        logger.error("Skipping narrative generation: API Key not configured")
        return "UNKNOWN", "API key not configured."
        
    prompt = f"""
    You are a financial analyst reviewing a batch of transactions.
    Based on the following aggregated data, determine a single RISK LEVEL (LOW, MEDIUM, HIGH) and provide a concise 2-3 sentence narrative summarizing the findings.
    
    Data:
    - Total Spend (INR): {total_spend_inr}
    - Total Spend (USD): {total_spend_usd}
    - Top Merchants: {top_merchants}
    - Anomaly Count: {anomaly_count}
    
    Respond STRICTLY in the following format:
    RISK_LEVEL: [LOW/MEDIUM/HIGH]
    NARRATIVE: [Your narrative here]
    """
    
    max_retries = 3
    
    try:
        model_name = 'gemini-3.5-flash'
        model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized model: {model_name} for narrative generation")
    except Exception as e:
        logger.error(f"Error initializing Gemini model for narrative: {str(e)}", exc_info=True)
        return "UNKNOWN", f"Error initializing model: {str(e)}"
        
    for attempt in range(max_retries):
        try:
            logger.info(f"Gemini narrative generation attempt {attempt + 1}/{max_retries}")
            
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            
            logger.info(f"Gemini raw narrative response: {raw_text}")
            
            lines = raw_text.split('\n')
            risk_level = "UNKNOWN"
            narrative = "No narrative provided."
            
            for line in lines:
                if line.upper().startswith("RISK_LEVEL:"):
                    risk_level = line.split(":", 1)[1].strip()
                elif line.upper().startswith("NARRATIVE:"):
                    narrative = line.split(":", 1)[1].strip()
            
            if risk_level != "UNKNOWN":
                logger.info(f"Successfully generated narrative. Risk Level: {risk_level}. Successful Gemini response: {raw_text}")
                return risk_level, narrative
                
        except Exception as e:
            logger.error(f"Gemini API narrative request failed on attempt {attempt + 1}: {str(e)}", exc_info=True)
            if attempt == max_retries - 1:
                return "UNKNOWN", f"Failed after {max_retries} attempts: {str(e)}"
            time.sleep(1)
            
    return "UNKNOWN", "Failed to generate narrative."
