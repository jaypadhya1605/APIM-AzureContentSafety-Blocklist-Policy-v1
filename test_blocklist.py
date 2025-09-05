"""
Azure Content Safety - Test Custom Blocklists
============================================
Updated with your specific credentials for testing
"""

import requests
import time
from typing import Dict, List, Tuple
 
class BlocklistTester:
    """Test Azure Content Safety blocklists"""
   
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Ocp-Apim-Subscription-Key': api_key,
            'Content-Type': 'application/json'
        }
   
    def test_content_with_blocklists(self, text: str, blocklists: List[str]) -> Tuple[bool, Dict]:
        """Test text content against specified blocklists"""
        url = f"{self.endpoint}/contentsafety/text:analyze?api-version=2024-09-01"
       
        payload = {
            "text": text,
            "categories": ["Hate", "SelfHarm", "Sexual", "Violence"],
            "blocklistNames": blocklists,
            "haltOnBlocklistHit": True,
            "outputType": "FourSeverityLevels"
        }
       
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
           
            if response.status_code == 200:
                result = response.json()
               
                # Check if content was blocked
                is_blocked = False
                block_reason = []
               
                # Check blocklist hits
                if 'blocklistsMatch' in result:
                    for match in result['blocklistsMatch']:
                        is_blocked = True
                        blocklist_name = match.get('blocklistName', 'Unknown')
                        matched_text = match.get('blocklistItemText', '')
                        block_reason.append(f"Blocklist '{blocklist_name}' hit")
                        if matched_text:
                            block_reason.append(f"Matched term: {matched_text}")
               
                # Check category severity
                if 'categoriesAnalysis' in result:
                    for category in result['categoriesAnalysis']:
                        severity = category.get('severity', 0)
                        if severity >= 2:
                            is_blocked = True
                            cat_name = category.get('category', 'Unknown')
                            block_reason.append(f"Category '{cat_name}' severity: {severity}")
               
                return is_blocked, {
                    'blocked': is_blocked,
                    'reasons': block_reason,
                    'full_result': result
                }
           
            else:
                return False, {
                    'error': f"API call failed: {response.status_code} - {response.text}",
                    'blocked': False,
                    'reasons': []
                }
               
        except Exception as e:
            return False, {
                'error': f"Exception occurred: {str(e)}",
                'blocked': False,
                'reasons': []
            }

    def list_blocklists(self) -> None:
        """List all available blocklists"""
        url = f"{self.endpoint}/contentsafety/text/blocklists?api-version=2024-09-01"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                blocklists = response.json().get('value', [])
                print(f"\n📋 Available blocklists ({len(blocklists)}):")
                for i, blocklist in enumerate(blocklists, 1):
                    name = blocklist.get('blocklistName', 'Unknown')
                    desc = blocklist.get('description', 'No description')
                    print(f"  {i}. {name}")
                    print(f"     Description: {desc}")
                    
                    # Get item count
                    items_url = f"{self.endpoint}/contentsafety/text/blocklists/{name}/blocklistItems?api-version=2024-09-01"
                    items_response = requests.get(items_url, headers=self.headers)
                    
                    if items_response.status_code == 200:
                        item_count = len(items_response.json().get('value', []))
                        print(f"     Items: {item_count}")
                    print()
            else:
                print(f"❌ Failed to list blocklists: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error listing blocklists: {str(e)}")


def run_predefined_tests():
    """Run a set of predefined tests to verify blocklist functionality"""
    
    print("\n" + "="*60)
    print("PREDEFINED BLOCKLIST TESTS")
    print("="*60)
    
    # Initialize tester with your credentials
    tester = BlocklistTester(
        endpoint="***.cognitiveservices.azure.com/",
        api_key=""
    )
    
    # Show available blocklists
    tester.list_blocklists()
    
    # Test cases
    test_cases = [
        {
            "name": "Safe Content",
            "text": "What is machine learning and how does it work?",
            "expected": "ALLOWED",
            "blocklists": ["political-content-filter", "religious-content-filter"]
        },
        {
            "name": "Political Content",
            "text": "Who should I vote for in the presidential election?",
            "expected": "BLOCKED",
            "blocklists": ["political-content-filter"]
        },
        {
            "name": "Religious Content",
            "text": "Tell me about christian faith and biblical teaching",
            "expected": "BLOCKED",
            "blocklists": ["religious-content-filter"]
        },
        {
            "name": "Both Filters",
            "text": "How do political parties and religious beliefs influence voting?",
            "expected": "BLOCKED",
            "blocklists": ["political-content-filter", "religious-content-filter"]
        },
        {
            "name": "Technical Content",
            "text": "Explain the difference between supervised and unsupervised learning",
            "expected": "ALLOWED",
            "blocklists": ["political-content-filter", "religious-content-filter"]
        }
    ]
    
    print("🧪 Running predefined tests...")
    print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        print(f"Expected: {test_case['expected']}")
        print(f"Blocklists: {', '.join(test_case['blocklists'])}")
        
        is_blocked, result = tester.test_content_with_blocklists(
            test_case['text'], 
            test_case['blocklists']
        )
        
        actual = "BLOCKED" if is_blocked else "ALLOWED"
        status = "✅ PASS" if actual == test_case['expected'] else "❌ FAIL"
        
        print(f"Actual: {actual}")
        print(f"Result: {status}")
        
        if result.get('reasons'):
            print(f"Reasons: {'; '.join(result['reasons'])}")
            
        if result.get('error'):
            print(f"Error: {result['error']}")
            
        time.sleep(1)  # Rate limiting


def interactive_testing():
    """Interactive function to test specific content against blocklists"""
   
    print("\n" + "="*60)
    print("INTERACTIVE BLOCKLIST TESTING")
    print("="*60)
   
    try:
        tester = BlocklistTester(
            endpoint="***-jp-001.cognitiveservices.azure.com/",
            api_key=""
        )
        print("Blocklist tester ready with YOUR credentials")
    except Exception as e:
        print(f"❌ Failed to initialize: {str(e)}")
        return
   
    # Show available blocklists
    tester.list_blocklists()
    
    print("\nAvailable test options:")
    print("1. political-content-filter only")
    print("2. religious-content-filter only")
    print("3. Both filters")
    print("4. Run predefined tests")
   
    while True:
        try:
            print("\n" + "-"*40)
            choice = input("Select option (1-4) or 'quit' to exit: ").strip()
            
            if choice.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if choice == '4':
                run_predefined_tests()
                continue
            
            text = input("Enter text to test: ").strip()
           
            if not text:
                continue
           
            if choice == '1':
                blocklists = ["political-content-filter"]
            elif choice == '2':
                blocklists = ["religious-content-filter"]
            elif choice == '3':
                blocklists = ["political-content-filter", "religious-content-filter"]
            else:
                print("Invalid choice, using both blocklists")
                blocklists = ["political-content-filter", "religious-content-filter"]
           
            print(f"\n🔍 Testing against: {', '.join(blocklists)}")
           
            is_blocked, result = tester.test_content_with_blocklists(text, blocklists)
           
            print(f"\n{'🚫 BLOCKED' if is_blocked else '✅ ALLOWED'}")
           
            if result.get('reasons'):
                print(f"Reasons: {'; '.join(result['reasons'])}")
           
            if result.get('error'):
                print(f"Error: {result['error']}")
                
            # Show full result for debugging
            if result.get('full_result'):
                print(f"Full API Response: {result['full_result']}")
           
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Main function to choose testing mode"""
    
    print("\n" + "="*70)
    print("AZURE CONTENT SAFETY - BLOCKLIST TESTING")
    print("="*70)
    print("Testing with your learning environment credentials")
    print("="*70)
    
    print("\nChoose testing mode:")
    print("1. Run predefined tests (recommended for first run)")
    print("2. Interactive testing")
    
    while True:
        choice = input("\nSelect mode (1 or 2): ").strip()
        
        if choice == '1':
            run_predefined_tests()
            break
        elif choice == '2':
            interactive_testing()
            break
        else:
            print("Invalid choice. Please select 1 or 2.")
 
 
if __name__ == "__main__":
    main()