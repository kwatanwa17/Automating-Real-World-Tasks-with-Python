#!/usr/bin/env python3

import json
import locale
import sys
import os
import reports
import emails


def load_data(filename):
    """Loads the contents of filename as a JSON file."""
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def format_car(car):
    """Given a car dictionary, returns a nicely formatted name."""
    return "{} {} ({})".format(
        car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
    """Analyzes the data, looking for maximums.

  Returns a list of lines that summarize the information.
  """
    locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
    max_revenue = {"revenue": 0}
    max_model_sales = {"total_sales": 0}
    year_sales = {}
    for item in data:
        # Calculate the revenue generated by this model (price * total_sales)
        # We need to convert the price from "$1234.56" to 1234.56
        item_price = locale.atof(item["price"].strip("$"))
        item_revenue = item["total_sales"] * item_price
        item_total_sales = item["total_sales"]
        car_year = item["car"]["car_year"]
        if item_revenue > max_revenue["revenue"]:
            item["revenue"] = item_revenue
            max_revenue = item
        # also handle max sales
        if item_total_sales > max_model_sales["total_sales"]:
            max_model_sales = item
        # also handle most popular car_year
        if car_year in year_sales.keys():
            year_sales[car_year] += item["total_sales"]
        else:
            year_sales[car_year] = item["total_sales"]

    # get max key and value
    max_year, max_total_sales = max(year_sales.items(), key=lambda x: x[1])

    summary = [
        "The {} generated the most revenue: ${}".format(
            format_car(max_revenue["car"]), max_revenue["revenue"]),
        "The {} had the most sales: {}".format(
            format_car(max_model_sales["car"]), max_model_sales["total_sales"]),
        "The most popular year was {} with {} sales.".format(
            max_year, max_total_sales)
    ]

    return summary


def cars_dict_to_table(car_data):
    """Turns the data in car_data into a list of lists."""
    table_data = [["ID", "Car", "Price", "Total Sales"]]
    for item in car_data:
        table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
    return table_data


def main(argv):
    """Process the JSON data and generate a full report out of it."""
    data = load_data("car_sales.json")
    summary = process_data(data)
    print(summary)
    filename = "./tmp/cars.pdf" if os.name == "nt" else "/tmp/cars.pdf"

    # turn this into a PDF report
    additional_info = "<br/>".join(summary)
    table_data = cars_dict_to_table(data)
    reports.generate(filename, "Sales summary for last month", additional_info, table_data)

    # send the PDF report as an email attachment
    sender = "automation@example.com"
    receiver = "{}@example.com".format(os.environ.get('USER'))
    subject = "Sales summary for last month"
    body = "\n".join(summary)

    message = emails.generate(sender, receiver, subject, body, filename)
    emails.send(message)


if __name__ == "__main__":
    main(sys.argv)
