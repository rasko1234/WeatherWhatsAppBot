import requests
import schedule
import time
from twilio.rest import Client
from datetime import datetime, timedelta

account_sid = 'your_twilio_account_sid'
auth_token = 'your_twilio_auth_token'
twilio_whatsapp_number = 'whatsapp:xxxxxxxxxxxx'
recipient_whatsapp_number = 'whatsapp:xxxxxxxxxx'

# Fetch weather forecast data for the upcoming week
def get_weather_forecast():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 40.5625,
        "longitude": 23.0,
        "hourly": "temperature_2m,precipitation",
        "timezone": "Europe/Athens",
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        forecast_data = response.json()
        return forecast_data
    else:
        print("Error fetching weather data.")
        return None



def process_weather_data(forecast_data):
    if forecast_data and 'hourly' in forecast_data:
        hourly_data = forecast_data['hourly']
        times = hourly_data['time']
        temperatures = hourly_data['temperature_2m']
        precipitations = hourly_data['precipitation']

        weekly_forecast = []
        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        # Calculate the start of the next week
        today = datetime.now()
        next_week_start = today + timedelta(days=(7 - today.weekday()))
        next_week_dates = [(next_week_start + timedelta(days=i)).date() for i in range(7)]


        for i, date in enumerate(next_week_dates):
            day_name = days_of_week[i]
            daily_forecast = f"Forecast for {day_name} ({date}):\nTemperature: "


            day_hours = []
            for j in range(len(times)):

                hour = int(times[j].split('T')[1].split(':')[0])
                day_of_week = datetime.strptime(times[j].split('T')[0], '%Y-%m-%d').date()

                if 8 <= hour < 16 and day_of_week == date:
                    temp = temperatures[j]
                    precip = precipitations[j]


                    day_hours.append(f"{hour}:00 -> Temperature: {temp}°C, Rain: {precip}mm")

            if day_hours:
                daily_forecast += "\n".join(day_hours)
            else:
                daily_forecast += "No rain hours for this day."

            weekly_forecast.append(daily_forecast)

        return weekly_forecast
    else:
        return ["No valid data available."]



def send_weather_forecast_whatsapp(message):
    client = Client(account_sid, auth_token)

    try:
        max_message_length = 1600
        while len(message) > max_message_length:
            part = message[:max_message_length]
            message = message[max_message_length:]

            client.messages.create(
                body=part,
                from_=twilio_whatsapp_number,
                to=recipient_whatsapp_number
            )


        client.messages.create(
            body=message,
            from_=twilio_whatsapp_number,
            to=recipient_whatsapp_number
        )

        print("WhatsApp message(s) sent successfully.")
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")



def send_weather_forecast():
    # Fetch weather data
    forecast_data = get_weather_forecast()


    weather_forecast = process_weather_data(forecast_data)


    for daily_message in weather_forecast:
        send_weather_forecast_whatsapp(daily_message)



schedule.every().monday.at("06:00").do(send_weather_forecast)


while True:
    schedule.run_pending()
    time.sleep(1)
