This project demonstrates the use of OpenWeatherMap API to obtain geolocation and weather data based on user inputs.
It showcases input validation, error handling, and the retrieval of specific information from JSON responses.

The project is divided into four functions:

    weather_fetcher(coords): This function takes latitude and longitude coordinates as input. It prompts the user
                             to select the unit of measurement for temperature (Fahrenheit, Celsius, or Kelvin).
                             Based on the selected unit, it constructs the appropriate API URL and makes a request
                             to the OpenWeatherMap API to retrieve weather data for the specified location. The API
                             response is then parsed to extract the relevant weather information, such as the
                             location name, weather description, temperature, and feels-like temperature. Finally,
                             the weather information is printed in a readable format for the user.
    
    city_state_locator(): This function prompts the user to enter a state and city. It constructs a URL with the
                          provided city and state information and makes an API request to the OpenWeatherMap API
                          to retrieve geolocation data for the specified location. The latitude and longitude of
                          the location are then extracted from the API response and returned.

    zip_locator(): This function prompts the user to enter a zip code. It validates the input to ensure it is a
                   valid zip code. If the zip code is valid, it constructs a URL with the zip code and makes an
                   API request to the OpenWeatherMap API to retrieve geolocation data for that zip code. The
                   latitude and longitude of the location are extracted from the API response and returned by the
                   function.
                   
    main(): This is the main entry point of the application. It displays a welcome message and prompts the user to
            select whether they want to perform a weather lookup using a city name or a zip code. Based on the
            selection, it calls the respective functions (city_state_locator() or zip_locator()) to obtain the
            coordinates for the location. Then, it calls the weather_fetcher() function to fetch and display the
            weather information. After each weather lookup, the user is given the option to continue with another
            search or exit the program.

This project also handles exceptions that may occur during the API requests and JSON parsing processes. It will provide error
messages to the user if any issues arise, such as invalid inputs, errors during the API request, or invalid JSON responses.
