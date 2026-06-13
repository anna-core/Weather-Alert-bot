#Weather-Alert Bot
import os
import requests
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage


#Fetch credentials from environment variables
OWM_API_KEY = os.getenv("OWM_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


def get_weather_data(city="Thiruvananthapuram"):
    """Fetch weather from OpenWeatherMap and return temp, condition, and text."""
    if not OWM_API_KEY:
        return None,None,"Weather unavailable (API Key missing)"  
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"].capitalize()
        weather_text = f"{temp}°C, {description}"
        return temp, condition, weather_text
    except Exception as e:
        return None, None, f"Weather unavailable ({e})"

def get_quote():
    """Fetch a random motivational quote from ZenQuotes."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f'"{data[0]["q"]}" - {data[0]["a"]}'
    except Exception as e:
        return f"Quote unavailable ({e})"

def send_email_alert(city, temp, condition):
    if not all([EMAIL_ADDRESS, EMAIL_PASSWORD, RECEIVER_EMAIL]):
        print("Email credentials missing. Skipping email alert.")
        return

    msg =EmailMessage()
    msg['Subject'] = f"Weather Alert for {city}!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    
    body = (
        f"Extreme weather conditions detected in {city}.\n\n"
        f"Current Temperature: {temp}°C\n"
        f"Condition: {condition}\n\n"
        "Stay safe today!"
    )
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def build_summary():
    """Assemble the summary and trigger alerts if necessary."""
    today = date.today().strftime("%A, %d %B %Y")
    city = "Thiruvananthapuram"
    
    # Fetch Data
    temp, condition, weather_text = get_weather_data(city)
    quote=get_quote()

    # Check for Alert Conditions(>35°C or Rain)
    if temp is not None and condition is not None:
        if temp > 35 or "rain" in condition.lower():
            print(f"Alert conditions met! Temp: {temp}°C,Condition: {condition}.")
            send_email_alert(city, temp, condition)

    summary = f"""
    WEATHER ALERT BOT - Daily Summary
    {today}
    -----------------------------------------------
    WEATHER ({city})
    {weather_text}
    -----------------------------------------------
    TODAY'S QUOTE
    {quote}
    -----------------------------------------------
    """
    return summary


def run():
    """Main entry point.Called by GitHub Actions."""
    summary = build_summary()
    print(summary)

    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    print("Weather Alert Bot ran successfully.")


if __name__ == "__main__":
    run()