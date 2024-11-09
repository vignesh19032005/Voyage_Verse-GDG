import os
import json
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Optional
import urllib
import google.generativeai as genai
import re

FOURSQUARE_API_KEY =  #Use your own API Key
OPENCAGE_API_KEY = #Use your own API Key
NEWS_API_KEY = #Use your own API Key
GOOGLE_API_KEY = #Use your own API Key
FOURSQUARE_ENDPOINT = 'https://api.foursquare.com/v3/places/search'
OPENCAGE_ENDPOINT = 'https://api.opencagedata.com/geocode/v1/json'
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/everything'


genai.configure(api_key=GOOGLE_API_KEY)

BUDGET_PREFERENCES = ["Low", "Medium", "High", "Luxury"]

places_data = {
    "attractions": {
        "historical": {
            "Low": ["Public museums", "Historical walking tours", "Heritage sites"],
            "Medium": ["Guided museum tours", "Historical monuments with guided tours"],
            "High": ["Private historical tours", "Exclusive museum experiences"],
            "Luxury": ["Private after-hours museum tours", "VIP historical experiences"]
        },
        "natural": {
            "Low": ["Public parks", "Nature trails", "Public beaches"],
            "Medium": ["Guided nature walks", "Boat tours", "National parks"],
            "High": ["Private nature tours", "Exclusive hiking experiences"],
            "Luxury": ["Helicopter nature tours", "Private island experiences"]
        },
        "cultural": {
            "Low": ["Local markets", "Public cultural centers", "Street performances"],
            "Medium": ["Cultural shows", "Art galleries", "Cooking classes"],
            "High": ["Private cultural experiences", "VIP art gallery tours"],
            "Luxury": ["Private cultural performances", "Exclusive artistic experiences"]
        }
    },
    "restaurants": {
        "local": {
            "Low": ["Street food", "Local cafes"],
            "Medium": ["Mid-range local restaurants"],
            "High": ["Fine dining local cuisine"],
            "Luxury": ["Michelin-starred local restaurants"]
        },
        "vegetarian": {
            "Low": ["Vegetarian cafes", "Food courts"],
            "Medium": ["Casual vegetarian restaurants"],
            "High": ["Upscale vegetarian restaurants"],
            "Luxury": ["Premium vegetarian fine dining"]
        },
        "non_vegetarian": {
            "Low": ["Fast food", "Food courts"],
            "Medium": ["Casual dining restaurants"],
            "High": ["Fine dining restaurants"],
            "Luxury": ["Michelin-starred restaurants"]
        }
    },
    "accommodations": {
        "Low": ["Hostels", "Budget hotels", "Guesthouses"],
        "Medium": ["3-star hotels", "Boutique hotels"],
        "High": ["4-star hotels", "Premium boutique hotels"],
        "Luxury": ["5-star hotels", "Luxury resorts"]
    }
}

DIETARY_PREFERENCES = ["Vegetarian", "Non-Vegetarian", "Both"]
TRAVEL_TYPES = ["Adventure", "Cultural", "Nature", "Religious", "Shopping", "Heritage", "Relaxation",
                "Wildlife", "Photography", "Food & Culinary", "Architecture", "Historical", "Beach",
                "Mountain", "Wellness", "Educational", "Festivals", "Nightlife", "Sports", "Local Experience"]

SCHEDULE = {
    "breakfast": "7:30 AM - 8:30 AM",
    "morning_attraction": "9:00 AM - 11:30 AM",
    "lunch": "12:00 PM - 1:00 PM",
    "afternoon_attraction": "1:30 PM - 4:00 PM",
    "evening_attraction": "4:30 PM - 7:00 PM",
    "dinner": "7:30 PM - 9:00 PM"
}

def get_budget_considerations(budget):
    """Return considerations based on budget preference."""
    considerations = {
        "Low": """- Focus on free and low-cost attractions
- Public transportation options
- Budget accommodation recommendations
- Street food and local markets
- Free walking tours and self-guided experiences
- Estimated daily budget : Give accordingly""",

        "Medium": """- Mix of paid attractions and free activities
- Combination of public and private transport
- Mid-range accommodation options
- Mix of local restaurants and casual dining
- Some guided tours and experiences
- Estimated daily budget: Give accordingly""",

        "High": """- Premium attractions and experiences
- Private transportation options
- 4-star accommodation recommendations
- Fine dining experiences
- Private guided tours
- Estimated daily budget: Give accordingly""",

        "Luxury": """- VIP and exclusive experiences
- Luxury private transportation
- 5-star and luxury accommodation
- Michelin-starred restaurants
- Private guides and customized experiences
- Estimated daily budget: Give accordingly"""
    }
    return considerations.get(budget, "Standard budget considerations apply")

def initialize_model():
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        raise Exception(f"Error initializing model: {str(e)}")
    
def get_model_response(places_data, place_name, days, travel_types,
                      group_size, dietary_preference, budget_preference,
                      custom_places):
    try:
        model = initialize_model()

        travel_types_str = " and ".join(travel_types)
        custom_places_section = "\nSpecifically Requested Places to Visit:\n" + "\n".join(f"- {place}" for place in custom_places) if custom_places else ""

        prompt = f"""
        Create a detailed {days}-day travel itinerary for {place_name} with:
        - Travel Types: {travel_types_str}
        - Group Size: {group_size} people
        - Dietary Preference: {dietary_preference}
        - Budget Level: {budget_preference}
        {custom_places_section}

        Schedule:
        - Breakfast: {SCHEDULE['breakfast']}
        - Morning Attraction: {SCHEDULE['morning_attraction']}
        - Lunch: {SCHEDULE['lunch']}
        - Afternoon Attraction: {SCHEDULE['afternoon_attraction']}
        - Evening Attraction: {SCHEDULE['evening_attraction']}
        - Dinner: {SCHEDULE['dinner']}

    1. For each day, ensure exactly three main attractions aligned with chosen travel types and budget level. Provide:
        - Attraction name and address
        - Brief description
        - Estimated visit duration
        - Group booking requirements
        - Dress code if any mandatory
        - Accessibility considerations
        - Cost estimate per person (within {budget_preference} budget range)

        Additional Considerations:
        {get_group_size_considerations(group_size)}

        Budget Considerations:
        {get_budget_considerations(budget_preference)}

        Dietary Considerations:
        {get_dietary_considerations(dietary_preference)}
    2. Feature exactly three main attractions per day, ensuring:
      - Activities align with the chosen travel type
      - Prioritize attractions in close proximity (within 10 km) to minimize travel time.
      - Attractions are suitable for the group size
      - No repetitions throughout the itinerary

    3. For each main attraction, provide:
      - Name and address
      - A brief description
      - Estimated duration of visit
      - Group booking requirements (if any)
      - Accessibility considerations
      - Cost estimate per person

    4. Recommend restaurants for each meal:
      - Two options for breakfast
      - Two options for lunch near the morning or afternoon attraction
      - Two options for dinner near the evening attraction
      Include for each restaurant:
      - Name and address
      - Cuisine type
      - Group accommodation capability
      - Price range
      - Reservation requirements

    5. Transportation recommendations:
      - Best mode of transport between locations
      - Group transportation options
      - Estimated travel times and costs
      - Parking information (if relevant)

    6. Additional Considerations:
      - Group booking requirements
      - Peak times to avoid crowds
      - Weather considerations
      - Safety tips specific to the group size and travel type
      - Local customs and etiquette
    
    7. Suggest 2-3 additional activity options that could be substituted or added if time allows, such as:
              - Local markets or shopping areas
              - Parks or green spaces
              - Cultural events or performances
              - Scenic viewpoints
              - Historical sites.
    
    8. All the places in the itinerary must be such that the user must be able to travel within stipulated time in the itinerary and for a smooth and best travel

    9. Recommend only Theme Parks if the number of days is more than 5 and also recommend Theme parks for a whole day

    10. And for each travel specify the approximate travelling time and accurate distance between the places.

    To ensure accuracy and relevance:
        - Cross-check information with reputable internet sources.
        - Verify the existence and popularity of each attraction.
        - Confirm all listed attractions are distinct and within the 50 km range from {place_name} center.

    Leverage your advanced language capabilities and knowledge to create an unforgettable travel experience, showcasing the best of {place_name} in a concise and easily navigable format.
    Make sure all the attractions in each day must be within 10 km range. And also the places most be user friendly for user to travel making the route more concise and suitable

    At the end of the each itinerary:
    1. Recommend 3 accommodation options suitable for the group size and travel type near:
      - City center
      - Main attractions
      - Transport hubs

    2. Provide:
      - Emergency contact numbers
      - Local guide recommendations
      - Group travel tips
      - Estimated total budget per person
      - Packing suggestions specific to the travel type

    Also include:
    - Give a complete and best summary for the {place_name}
    - Best time to visit for this type of travel
    - Local festivals or events during the visit
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        raise Exception(f"Error generating itinerary: {str(e)}")

def get_group_size_considerations(group_size):
    if group_size == 1:
        return "- Solo-friendly activities\n- Safety aspects for solo traveler\n- Social activities and group tours options\n- Flexible scheduling"
    elif group_size <= 4:
        return "- Balance activities for small group\n- Private transportation options\n- Intimate dining experiences\n- Mix of group and individual activities"
    else:
        return "- Group-friendly venues and activities\n- Group booking requirements\n- Larger transportation needs\n- Split group for certain activities"
    
def get_custom_places():
    custom_places = []
    print("\nEnter the places you want to visit (one per line). Press Enter twice when you're done:")
    while True:
        place = input().strip()
        if not place and custom_places:
            break
        elif place:
            custom_places.append(place)
    return custom_places

def get_dietary_considerations(preference):
    considerations = {
        "Vegetarian": """
        - Focus on pure vegetarian restaurants
        - Include restaurants with clear veg/non-veg segregation
        - Consider local vegetarian specialties
        - Include international vegetarian cuisine options
        - Check for vegan options if needed
        - Verify ingredient preparation methods
        """,
        "Non-Vegetarian": """
        - Include restaurants with diverse meat options
        - Focus on local meat specialties
        - Consider seafood options where available
        - Include international cuisine options
        - Verify halal/kosher requirements if needed
        """,
        "Both": """
        - Include restaurants with both veg and non-veg options
        - Ensure clear segregation of veg/non-veg food
        - Focus on restaurants with diverse menu options
        - Consider group dining preferences
        - Include international cuisine options
        """
    }
    return considerations.get(preference, "Standard dietary considerations apply")

def save_itinerary(place_name, itinerary):
    try:
        os.makedirs('itineraries', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"itineraries/{place_name.replace(' ', '')}{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Travel Itinerary for {place_name}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(itinerary)

        return filename
    except Exception as e:
        print(f"Error saving itinerary: {str(e)}")
        return None

def get_place_time(schedule):
        model = initialize_model()
        system_prompt = '''System Prompt: I'll give you the Itinerary and from that you must provide me a json output consisting places along with their respective days and timings.
        The output should follow the given format:
        {
            "day1": {
                "place1": {
                    "place": "Accurate Place Name",
                    "time": "HH:MM",
                    "address": "Full accurate ADDRESS",
                    "lat": "Latitude",
                    "lng": "Longitude",
                    "Description":"2 line description",
                    "recommended_restaurants": [
                        {"name": "Restaurant Name 1", "address": "Restaurant Address 1","lat":"Latitude","lon":"Longitude"},
                        {"name": "Restaurant Name 2", "address": "Restaurant Address 2","lat":"Latitude","lon":"Longitude"}
                        ]
                    "recommended_hotels":[
                      {"name": "Hotel Name 1", "address": "Hotel Address 1","lat":"Latitude","lon":"Longitude"},
                      {"name": "Hotel Name 2", "address": "Hotel Address 2","lat":"Latitude","lon":"Longitude"}
                    ],
                },
                "place2": {
                    "place": "Place Name",
                    "time": "HH:MM",
                    "lat": "Latitude",
                    "lng": "Longitude",
                    "address": "Full accurate ADDRESS",
                    "Description":"2 line description",
                    "recommended_restaurants": [
                        {"name": "Restaurant Name 1", "address": "Restaurant Address 1","lat":"Latitude","lon":"Longitude"},
                        {"name": "Restaurant Name 2", "address": "Restaurant Address 2","lat":"Latitude","lon":"Longitude"}
                    ],
                    "recommended_hotels":[
                      {"name": "Hotel Name 1", "address": "Hotel Address 1","lat":"Latitude","lon":"Longitude"},
                      {"name": "Hotel Name 2", "address": "Hotel Address 2","lat":"Latitude","lon":"Longitude"}
                    ]
                }
            },
            "day2": {
                ...
            }
        }
        Ensure that the "address" field contains the full and accurate address for each place and restaurant.
        Schedule: '''

        place_time_output = model.generate_content(system_prompt + schedule)

        # try:
        #     json_start = place_time_output.index('{')
        #     json_end = place_time_output.rindex('}') + 1
        #     json_output = place_time_output[json_start:json_end]
        #     place_time_json = json.loads(json_output)
        # except (ValueError, json.JSONDecodeError):
        #     raise ValueError("Failed to parse JSON output from the model.")

        # return place_time_json
        try:
            match = re.search(r'\{.*\}', place_time_output, re.DOTALL)
            if match:
                json_output = match.group(0)
                place_time_json = json.loads(json_output)
            else:
                raise ValueError("Failed to find JSON structure in the output.")
        except (ValueError, json.JSONDecodeError):
            raise ValueError("Failed to parse JSON output from the model.")


def is_itinerary_request(user_input):
    itinerary_keywords = ['itinerary', 'plan', 'schedule', 'trip plan', 'travel plan']
    return any(re.search(rf'\b{word}\b', user_input.lower()) for word in itinerary_keywords)

def travel_chatbot(user_input):
    genai.configure(api_key='AIzaSyA5phyiuSfCw565e2W_hBRn_qcYH-PXFaY')

    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    
    if is_itinerary_request(user_input):
        return "Chatbot: For detailed itinerary planning or trip schedules, please visit our main page, where you can generate custom itineraries. 🗺️"

    travel_prompt = f"You are a helpful tours and travel assistant. 🧳 Provide information and suggestions related to travel. Use catchy emojis wherever needed. User query: {user_input}"

    response = model.generate_content(travel_prompt)

    return response.text

def main():
    try:
        place_name = input("Enter a location name: ")
        while True:
            try:
                days = int(input("Enter the number of days for the itinerary: "))
                if days <= 0:
                    print("Please enter a positive number of days.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        print("\nAvailable Travel Types:")
        for i, travel_type in enumerate(TRAVEL_TYPES, 1):
            print(f"{i}. {travel_type}")

        selected_travel_types = []
        while True:
            try:
                selections = input("\nSelect travel types (e.g., '1,3,5'): ").strip().split(',')
                indices = [int(x.strip()) - 1 for x in selections]
                selected_travel_types = [TRAVEL_TYPES[i] for i in indices if 0 <= i < len(TRAVEL_TYPES)]
                if selected_travel_types:
                    break
                print("Please select valid numbers.")
            except ValueError:
                print("Please enter valid numbers separated by commas.(Enter NIL if nothing)")

        custom_places = get_custom_places()

        while True:
            try:
                group_size = int(input("Enter group size: "))
                if group_size <= 0:
                    print("Please enter a positive number for group size.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        print("\nDietary Preferences:")
        for i, pref in enumerate(DIETARY_PREFERENCES, 1):
            print(f"{i}. {pref}")
        dietary_preference = DIETARY_PREFERENCES[int(input("\nSelect dietary preference (1-3): ")) - 1]

        print("\nBudget Preferences:")
        for i, budget in enumerate(BUDGET_PREFERENCES, 1):
            print(f"{i}. {budget}")
        budget_preference = BUDGET_PREFERENCES[int(input("\nSelect budget preference (1-4): ")) - 1]

        print("\nGenerating itinerary...")
        itinerary = get_model_response(places_data, place_name, days, selected_travel_types,
                                     group_size, dietary_preference, budget_preference, custom_places)
        print("\n=== Generated Itinerary ===\n")
        print(itinerary)

        
        #place_time = get_place_time(itinerary)
        
        #print("\nPlaces with Day and Time Information:")
        #json_output = json.dumps(place_time, indent=4)
        #print(f"placetime: {place_time}")

        #urls = {
        #    place_info['place']: f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(place_info['address'])}"
        #    for day in place_time.values() for place_info in day.values()
        #}

        #print(urls)

        saved_file = save_itinerary(place_name, itinerary)
        if saved_file:
            print(f"\nItinerary saved to {saved_file}")
        else:
            print("\nItinerary could not be saved.")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == 'exit':
                print("Chatbot: Thank you for using the Tours and Travel Chatbot. Safe travels! ✈️")
                break
            
            response = travel_chatbot(user_input)
            print(response)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

