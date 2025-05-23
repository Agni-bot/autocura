# Gemini API Key Configuration Handler
import json
import os

CONFIG_DIR = "/home/ubuntu/will_system/configs"
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys_config.json")

class GeminiConfigHandler:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)

    def save_api_key(self, api_key):
        """Saves the Gemini API key to the config file."""
        try:
            data = {}
            if os.path.exists(API_KEYS_FILE):
                with open(API_KEYS_FILE, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        print(f"Warning: {API_KEYS_FILE} is corrupted. Will overwrite.")
                        data = {}
            
            data["GEMINI_API_KEY"] = api_key
            
            with open(API_KEYS_FILE, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Gemini API key saved to {API_KEYS_FILE}")
            return True
        except Exception as e:
            print(f"Error saving API key: {e}")
            return False

    def load_api_key(self):
        """Loads the Gemini API key from the config file or environment variable."""
        # First, try to load from environment variable
        env_api_key = os.environ.get("GEMINI_API_KEY")
        if env_api_key:
            print("Loaded Gemini API key from environment variable.")
            return env_api_key

        # If not in env, try to load from config file
        if os.path.exists(API_KEYS_FILE):
            try:
                with open(API_KEYS_FILE, "r") as f:
                    data = json.load(f)
                    api_key = data.get("GEMINI_API_KEY")
                    if api_key:
                        print(f"Loaded Gemini API key from {API_KEYS_FILE}")
                        return api_key
            except Exception as e:
                print(f"Error loading API key from file: {e}")
        
        print("Gemini API key not found in config file or environment variables.")
        return None

    def get_api_key_from_user(self):
        """Prompts the user to enter their Gemini API key."""
        api_key = input("Please enter your Gemini API Key: ")
        if api_key:
            self.save_api_key(api_key)
            return api_key
        return None

    def ensure_api_key_is_set(self):
        """Ensures the API key is set, prompting user if necessary."""
        api_key = self.load_api_key()
        if not api_key:
            print("Gemini API Key is not set.")
            # In a real application, you might call get_api_key_from_user()
            # but for automated Manus, direct input prompt is not ideal.
            # This function will primarily rely on pre-configuration or env vars.
            # For now, we'll just return None if not found, and client will raise error.
            pass # Or raise an error, or prompt if in an interactive context
        return api_key

# Example usage (for testing purposes)
if __name__ == '__main__':
    handler = GeminiConfigHandler()
    
    # Simulate checking if key is set
    key = handler.ensure_api_key_is_set()
    if not key:
        print("API Key not set. Simulating user input...")
        # In a real CLI, you'd uncomment the next line
        # key = handler.get_api_key_from_user()
        # For this test, let's simulate saving one if it wasn't found
        if not os.path.exists(API_KEYS_FILE):
             handler.save_api_key("TEST_API_KEY_FROM_CONFIG_HANDLER_EXAMPLE")
             key = handler.load_api_key()

    if key:
        print(f"Using API Key: {key}")
    else:
        print("Failed to obtain API Key.")

    # Test saving a new key (this would overwrite if run multiple times)
    # handler.save_api_key("ANOTHER_TEST_KEY_12345")
    # loaded_key = handler.load_api_key()
    # print(f"Newly loaded key: {loaded_key}")

