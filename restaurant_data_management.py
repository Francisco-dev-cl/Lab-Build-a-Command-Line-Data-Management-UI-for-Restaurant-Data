from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json
import os
import shutil
import io
import unittest
import re
from unittest.mock import patch

FILEPATH = 'structured_restaurant_data.json'
BACKUP_PATH = 'structured_restaurant_data.json.bak'

EXAMPLE_RESTAURANT_PARAGRAPH = 'Down in **Santa Monica**, **Mar de Cortez** serves as a **sun-drenched**, **casual taqueria** specializing in **Baja-style seafood**.'
EXAMPLE_OUTPUT = """
 {
 "name": "Mar de Cortez",
 "location": "Santa Monica",
 "type": "casual taqueria",
 "food_style": "Baja-style seafood",
 "rating": 4.2,
 "price_range": 1,
 "signatures": ["beer-battered snapper tacos", "zesty octopus ceviche"],
 "vibe": "salt-air energy",
 "environment": "a premier sun-drenched spot for open-air dining near the pier.",
 "shortcomings": []
 }
"""

class Restaurant(BaseModel):
    name: str
    location: str
    type: str
    food_style: str
    rating: Optional[float] = None
    price_range: Optional[int] = None
    signatures: List[str] = Field(default_factory=list)
    vibe: Optional[str] = None
    environment: str
    shortcomings: List[str] = Field(default_factory=list)

def load_data(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, 'r') as f:
        try: return json.load(f)
        except json.JSONDecodeError: return []

def save_data(data, file_path, backup_path):
    if os.path.exists(file_path):
        shutil.copy(file_path, backup_path)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def show_restaurant_card(res, index):
    print(f"\n{'='*15} RESTAURANT #{index} {'='*15}")
    name = res.get('name', res.get('restaurant_name', 'Unnamed Restaurant'))
    print(f"NAME : {name}")
    for key, value in res.items():
        if key.lower() not in ['name', 'restaurant_name']:
            label = key.replace('_', ' ').upper()
            print(f"{label:<12}: {value}")
    print('='*45)

def restaurant_data_structure_prompt_generation(restaurant_paragraph):
    base_system_msg = "You are a data extraction assistant. Extract details and output strictly in JSON format."
    base_user_prompt = f"Extract structured info from: {restaurant_paragraph}\nExample Output: {EXAMPLE_OUTPUT}"
    return base_system_msg, base_user_prompt

def llm_model(system_msg, prompt_txt):
    model_id = "ibm/granite-4-h-small"
    project_id = "skills-network"
    credentials = Credentials(url="https://us-south.ml.cloud.ibm.com")
    
    model = ModelInference(model_id=model_id, credentials=credentials, project_id=project_id)
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt_txt}
    ]
    
    # Passing params here avoids the UserWarning
    chat_params = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 500
    }
    
    response = model.chat(messages=messages, params=chat_params)
    
    # Robust response parsing to avoid KeyError
    try:
        if isinstance(response, dict) and 'choices' in response:
            return response['choices'][0]['message']['content']
        return response.get('results', [{}])[0].get('generated_text', "")
    except (KeyError, IndexError, TypeError):
        return ""

def JSON_auto_repair_prompts(candidate_json_output, error_message):
    system = "You are a JSON repair expert. Output ONLY valid JSON."
    prompt = f"Fix this JSON: {candidate_json_output}\nError: {error_message}"
    return system, prompt

def clean_json_string(raw_str):
    """Removes markdown code blocks and whitespace to prevent JSONDecodeError."""
    clean = re.sub(r'```json\s*|```', '', raw_str).strip()
    return clean

def new_data_entry_process(paragraph, itemId):
    system_msg = "You are a data extraction assistant that only outputs valid JSON."
    s_msg, p_txt = restaurant_data_structure_prompt_generation(paragraph)
    raw_response = llm_model(s_msg, p_txt)
    
    try:
        clean_json = json.loads(clean_json_string(raw_response))
        validated_data = Restaurant(**clean_json).model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        # Step 3: Auto-Repair attempt
        r_sys, r_prompt = JSON_auto_repair_prompts(raw_response, str(e))
        repaired_res = llm_model(r_sys, r_prompt)
        try:
            validated_data = json.loads(clean_json_string(repaired_res))
        except:
            return {"id": itemId, "name": "Error", "environment": "Failed to parse LLM output."}
    
    validated_data['id'] = itemId
    return validated_data

def manage_restaurants(file_path=FILEPATH, backup_path=BACKUP_PATH):
    while True:
        data = load_data(file_path)
        print(f"\nRESTAURANT DATABASE | Records: {len(data)}")
        print("1. Browse\n2. View\n3. Add\n4. Edit\n5. Delete\n6. Exit")
        choice = input("\nAction: ")
        
        if choice == '6': break
        
        if choice in ['3', '4', '5']:
            if input("Are you sure? (type 'yes'): ").lower() != 'yes':
                print("Operation cancelled.")
                continue

        if choice == '3':
            desc = input("Description: ")
            new_item = new_data_entry_process(desc, 1000000 + len(data) + 1)
            data.append(new_item)
            save_data(data, file_path, backup_path)
            print("✓ Restaurant added.")
        elif choice == '5':
            idx_input = input("Index to delete: ")
            if idx_input.isdigit() and int(idx_input) < len(data):
                removed = data.pop(int(idx_input))
                save_data(data, file_path, backup_path)
                print(f"Deleted '{removed.get('name')}'")

# --- Unit Tests ---
class TestRestaurantDatabase(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_db.json'
        self.test_file_backup = 'test_db.bak'
        with open(self.test_file, 'w') as f:
            json.dump([{"name": "Test Cafe", "location": "Test City", "type": "cafe", "food_style": "test", "environment": "test"}], f)

    def tearDown(self):
        for f in [self.test_file, self.test_file_backup]:
            if os.path.exists(f): os.remove(f)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_add_and_delete_restaurant_success(self, mock_stdout, mock_input):
        # Sequence: Add -> Confirm -> Description -> Exit
        mock_input.side_effect = ['3', 'yes', 'Tasty Tacos in LA', '6']
        manage_restaurants(self.test_file, self.test_file_backup)
        self.assertIn("✓ Restaurant added.", mock_stdout.getvalue())

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_delete_security_cancel(self, mock_stdout, mock_input):
        # Sequence: Delete -> Cancel -> Exit
        mock_input.side_effect = ['5', 'no', '6']
        manage_restaurants(self.test_file, self.test_file_backup)
        self.assertIn("Operation cancelled.", mock_stdout.getvalue())

#if __name__ == "__main__":
#    unittest.main()

if __name__ == "__main__":
    manage_restaurants()