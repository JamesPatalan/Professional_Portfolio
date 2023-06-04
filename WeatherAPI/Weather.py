import requests


# Intakes Lat/Lon from other functions. Outputs weather information.
def weather_fetcher(coords):
    lat = coords[0]
    lon = coords[1]

    while True:
        key = 'ac016926573221d05a44c407edeb1997'
        print('Would you like temperature displayed in Fahrenheit, Celsius or Kelvin?')
        units = input('Please enter "F", "C" or "K": ')

        # Allows user to select the unit of measurement
        if units.lower() == 'f':
            url3 = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=imperial'
        elif units.lower() == 'c':
            url3 = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric'
        elif units.lower() == 'k':
            url3 = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}'
        else:
            print('Invalid choice, please try again.')
            continue

        try:
            response = requests.get(url3)
            response_json = response.json()

            if not response_json:
                print('Unable to retrieve weather data, please try again.')
                continue

            name = response_json['name']
            description = response_json['weather'][0]['description']
            temp = response_json['main']['temp']
            feels_like = response_json['main']['feels_like']

            # Prints weather in a readable format for the user
            print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
            print(f'Currently in {name}, the weather is {description}.')
            print(f'The temperature is {temp}, but it feels like {feels_like}')

            break

        # Handles exceptions made during API request
        except requests.exceptions.RequestException as exc:
            print(f'An error occurred during the request: {exc}')
        # Handles exceptions made during JSON parsing
        except ValueError:
            print('Received invalid JSON response from API.')


# Intakes user input ZIP. Outputs Lat/Lon.
def zip_locator():
    while True:
        key = 'ac016926573221d05a44c407edeb1997'
        zip_code = input('Enter zip code: ')

        # Validate inputs
        if not zip_code.isdigit():
            print('Invalid zip code, please try again.')
            continue

        url2 = f'http://api.openweathermap.org/geo/1.0/zip?zip={zip_code},US&appid={key}'

        try:
            response = requests.get(url2)
            response_json = response.json()

            if not response_json:
                print('Unable to retrieve geolocation data, please check the zip code.')
                continue

            return response_json['lat'], response_json['lon']

        # Handles exceptions made during API request
        except requests.exceptions.RequestException as exc:
            print(f'An error occurred during the request: {exc}')
        # Handles exceptions made during JSON parsing
        except ValueError:
            print('Received invalid JSON response from API.')


# Intakes user input City/State. Outputs Lat/Lon.
def city_state_locator():
    while True:
        key = 'ac016926573221d05a44c407edeb1997'
        city_name = input('Enter city: ')
        state_code = input('Enter state: ')

        # Validate inputs
        if not state_code.isalpha() or not city_name.isalpha():
            print('Invalid city or state, please try again.')
            continue

        url1 = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},US&limit=3&appid={key}'

        try:
            response = requests.get(url1)
            response_json_dirty = response.json()

            if not response_json_dirty:
                print('Unable to retrieve geolocation data, please check the city and state names.')
                continue

            response_json = response_json_dirty[0]
            return response_json['lat'], response_json['lon']

        # Handles exceptions made during API request
        except requests.exceptions.RequestException as exc:
            print(f'An error occurred during the request: {exc}')
        # Handles exceptions made during JSON parsing
        except ValueError:
            print('Received invalid JSON response from API.')


def main():
    print('~~ United States Weather Lookup ~~')

    # Loops as many times as user would like
    while True:
        print('Would you like to lookup weather using city name or zip code?')
        selection = input('Enter "city" or "zip": ')

        if selection == 'city':
            coords = city_state_locator()
            weather_fetcher(coords)
        elif selection == 'zip':
            coords = zip_locator()
            weather_fetcher(coords)
        else:
            print('Invalid selection. Please try again.')

        run = input('Input any key to make another search, or input "stop" to exit: ')
        if run.lower() == 'stop':
            break


if __name__ == '__main__':
    main()
