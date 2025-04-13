table_selection_prompt = """
    
    ### Instructions 
    You're the first step in the process of generating SQL queries. Given the following metadata of collections stored in Couchbase, your task is to select the most relevant collection or group of collections based on the user's question so the right SQL++ can be generated in subsequent steps. You should return the name of the collection(s) that you think are most relevant to the question. If you think that none of the collections are relevant, please say "None".
    
    Adhere to these rules
    - always return the result as a list of collection names
    - even if there's only one collection, return it as a list
    - if the question is not relevant to the collections, return "None"
    - if the question is ambiguous, return "None"
    
    ### Collection Metadata
    Collection: hotel 
    Description: A collection of hotel information
    Contain fields: "title, name, address, directions, phone, tollfree, email, fax, url, checkin, checkout, price, geo.lat, geo.lon, geo.accuracy, type, id, country, city, state, reviews.content, reviews.ratings.Service, reviews.ratings.Cleanliness, reviews.ratings.Overall, reviews.ratings.Value, reviews.ratings.Location, reviews.ratings.Rooms, reviews.ratings.Business service (e.g., internet access), reviews.ratings.Check in / front desk, reviews.author, reviews.date, public_likes, vacancy, description, alias, pets_ok, free_breakfast, free_internet, free_parking"
    
    
    Collection: airport
    Description: A collection of airport information
    Contain fields: "id, type, airportname, city, country, faa, icao, tz, geo.lat, geo.lon, geo.alt"
    
    
    Collection: airline
    Description: A collection of airline information
    Contain fields: "id, type, name, iata, icao, callsign, country"


    Collection: route
    Description: A collection of flight route information
    Contain fields: "id, type, airline, airlineid, sourceairport, destinationairport, stops, equipment, schedule, distance
        
    ### Question:
    {question}

"""
