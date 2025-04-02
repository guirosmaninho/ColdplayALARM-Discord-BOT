import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# URL of the Coldplay tour page
url = "https://www.coldplay.com/tour/"

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all concert cards
    concert_cards = soup.find_all("div", class_="tour-card")

    # Extract concert details
    concert_data = []
    for card in concert_cards:

        #Extract the region
        region_data = card.get("data-filter", "Unknown")

        if region_data == "row":
            region = "ASIA / AUSTRALIA"
        elif region_data == "eu":
            region = "UK / EUROPE"
        elif region_data == "us":
            region = "USA / CA"
        elif region_data == "lamerica":
            region = "LATIN AMERICA"
        else:
            region = "Unknown"

        # Extract the href link
        link_tag = card.find("a", class_="tour-card__anchor js-load-in")
        if link_tag and "href" in link_tag.attrs:
            href_link = link_tag["href"]  # Get the href attribute
        else:
            href_link = "Unknown"
        # Extract the date
        date_div = card.find("div", class_="tour-card__date")
        if date_div:
            raw_date = date_div.get_text(separator=" ", strip=True).replace("\n", " ").replace("  ", " ")

            # Convert the date to DD/MM/YYYY format
            try:
                date_obj = datetime.strptime(raw_date, "%B %d %Y")
                formatted_date = date_obj.strftime("%d/%m/%Y")  # Format as DD/MM/YYYY
            except ValueError:
                formatted_date = "Unknown"
        else:
            formatted_date = "Unknown"

        # Extract the stadium and city
        title_div = card.find("div", class_="tour-card__title")
        if title_div:
            stadium = title_div.find("h4").get_text(strip=True)
            city = title_div.get_text(strip=True).replace(stadium, "").strip()
        else:
            stadium = "Unknown"
            city = "Unknown"

            # Extract if it is sold out
            sold_out_span = card.find("span", class_="tour-card__button tour-card__button--inactive")
            if sold_out_span:
                text = sold_out_span.get_text(strip=True)
                if text == "SOLD OUT":
                    status = "Yes"
                else:
                    status = "No"

            else:
                status = "Unknown"

        # Extract if it is sold out
        sold_out_span = card.find("span", class_="tour-card__button tour-card__button--inactive")
        if sold_out_span:
            text = sold_out_span.get_text(strip=True)  # Get the text (e.g., "SOLD OUT")
            if text == "SOLD OUT":
                status = "Yes"
            else:
                status = "No"

        else:
            status = "Unknown"

        # Add the concert to the list
        concert_data.append({
            "date": formatted_date,
            "stadium": stadium,
            "city": city,
            "region": region,
            "soldout": status,
            "link": href_link
        })

    # Save the data to a JSON file
    with open("data/coldplay_concerts.json", "w") as f:
        json.dump(concert_data, f, indent=4)

    print("Concert data saved to coldplay_concerts.json")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")