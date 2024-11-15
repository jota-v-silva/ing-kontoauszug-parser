from pypdf import PdfReader
from pathlib import Path
import re
import pandas as pd
import argparse
from sys import stderr


def parse_ing_kontoauszug(file: Path) -> pd.DataFrame:
    """
    Parses a given Kontoauszug PDF file and returns its contents as a pandas DataFrame.

    Parameters:
        file (Path): The path to the kontoauszug PDF file.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed data from the kontoauszug PDF file. The DataFrame has three columns: 'date' (datetime), 'description' (str), and 'amount' (float).
    """
    reader = PdfReader(file)
    results = {"date": [], "description": [], "amount": []}
    amount_regex = re.compile(r"(-?(\d{1,3}(\.\d{3})*|\d+),\d{2})$")
    date_regex = re.compile(
        r"^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)[0-9]{2}"
    )

    for page in reader.pages:
        content = page.extract_text(0)

        for line in content.split("\n"):
            amount = amount_regex.search(line)
            if amount is not None:
                date = date_regex.search(line)
                if date is not None:
                    date = date.group(0)
                    amount = amount.group(0)
                    description = line[len(date) : -len(amount)].strip()

                    amount = float(amount.replace(".", "").replace(",", "."))
                    results["date"].append(date)
                    results["amount"].append(amount)
                    results["description"].append(description)
    data = pd.DataFrame(results)
    data["date"] = pd.to_datetime(data["date"], format="%d.%m.%Y")
    return data

def parse_ing_depotauszug(file: Path) -> pd.DataFrame:
    """
    Parses a given Depotauszug PDF file and returns its contents as a pandas DataFrame.

    Parameters:
        file (Path): The path to the PDF file.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed data from the depotauszug PDF file. 
        The DataFrame has 6 columns: 'date' (datetime), 'amount' (int), 'name' (str), ISIN ('str'), 'Price' (float), 'Market Value' (float).
    """
    reader = PdfReader(file)
    results = {"date": [], "name": [], "isin": [], "amount": [], "price": [], "market value": []}

    # Regex
    date_regex = re.compile(r"\bDepotauszug per\s+(\d{2}\.\d{2}\.\d{4})\b")
    name_regex = re.compile(r"\bStück\s+([^0-9]+?)\s+\d+(?:,\d+)?")
    isin_regex = re.compile(r"ISIN \(WKN\):\s+(.*?)\s+")
    amount_regex = re.compile(r"\b(\d+(?:,\d+)?)\s+Stück\b")
    price_regex = re.compile(r"(\d+(?:,\d+)?)\s+EUR(?!$)")
    market_regex = re.compile(r"EUR\s+(.*?)\s+EUR")

    for page in reader.pages:
        content = page.extract_text(0)
        for line in content.split("\n"):
            date = date_regex.search(line)
            name = name_regex.search(line)
            isin = isin_regex.search(line)
            amount = amount_regex.search(line)
            price = price_regex.search(line)
            market_value = market_regex.search(line)
            if date is not None:
                results["date"].append(date.group(1))
            if name is not None:
                results['name'].append(name.group(1))
            if isin is not None:
                results['isin'].append(isin.group(1))
            if amount is not None:
                results['amount'].append(float(amount.group(1).replace(".", "").replace(",", ".")))
            if price is not None:
                results['price'].append(float(price.group(1).replace(".", "").replace(",", ".")))
            if market_value is not None:
                results['market value'].append(float(market_value.group(1).replace(".", "").replace(",", ".")))

    data = pd.DataFrame(results)
    data["date"] = pd.to_datetime(data["date"], format="%d.%m.%Y")
    print(data)
    return data


def parse_ing_abrechnung(file: Path) -> pd.DataFrame:
    """
    Parses a given Abrechnung PDF file and returns its contents as a pandas DataFrame.

    Parameters:
        file (Path): The path to the PDF file.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed data from the Abrechnung PDF file. 
        The DataFrame has 6 columns: 'date' (datetime), 'amount' (int), 'name' (str), ISIN ('str'), 'Price' (float), 'Market Value' (float).
    """
    reader = PdfReader(file)
    results = {"date": [], "name": [], "isin": [], "order type": [], "order number": [],
         "trading venue": [], "execution time": [], "amount": [], "price": [], "total cost": []}

    # Regex
    date_regex = re.compile(r"\bDatum:\s+(\d{2}\.\d{2}\.\d{4})\b")
    name_regex = re.compile(r"(?<=Wertpapierbezeichnung )(.*?)(?=$|\n)")
    isin_regex = re.compile(r"(?<=ISIN \(WKN\) )(.*?)(?=$|\n)")
    order_type_regex = re.compile(r"(?<=Wertpapierabrechnung )(.*?)(?=$|\n)")
    order_number_regex = re.compile(r"(?<=Ordernummer )(.*?)(?=$|\n)")
    trading_venue_regex = re.compile(r"(?<=Handelsplatz )(.*?)(?=$|\n)")
    execution_time_regex = re.compile(r"(?<=um\s)(\d{2}:\d{2}:\d{2})(?=\s*Uhr)")
    amount_regex = re.compile(r"(?<=Nominale Stück )(.*?)(?=$|\n)")
    price_regex = re.compile(r"(?<=Kurs \(Festpreisgeschäft\) EUR )(.*?)(?=$|\n)")
    total_cost_regex = re.compile(r"(?<=Endbetrag zu Ihren Lasten EUR )(.*?)(?=$|\n)")

    for page in reader.pages:
        content = page.extract_text(0)
        for line in content.split("\n"):

            date = date_regex.search(line)
            name = name_regex.search(line)
            isin = isin_regex.search(line)
            order_type = order_type_regex.search(line)
            order_number = order_number_regex.search(line)
            trading_venue = trading_venue_regex.search(line)
            execution_time = execution_time_regex.search(line)
            amount = amount_regex.search(line)
            price = price_regex.search(line)
            total_cost = total_cost_regex.search(line)

            if date is not None:
                results["date"].append(date.group(1))
            if name is not None:
                results["name"].append(name.group(1))
            if isin is not None:
                results["isin"].append(isin.group(1))
            if order_type is not None:
                results["order type"].append(order_type.group(1))
            if order_number is not None:
                results["order number"].append(order_number.group(1))
            if trading_venue is not None:
                results["trading venue"].append(trading_venue.group(1))
            if execution_time is not None:
                results["execution time"].append(execution_time.group(1))
            if amount is not None:
                results["amount"].append(amount.group(1))
            if price is not None:
                results["price"].append(price.group(1).replace(".", "").replace(",", "."))
            if total_cost is not None:
                results["total cost"].append(total_cost.group(1).replace(".", "").replace(",", "."))

    data = pd.DataFrame(results)
    data["date"] = pd.to_datetime(data["date"], format="%d.%m.%Y")
    print(data)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path",
        metavar="INPUT",
        type=str,
        help="Can be a file or a directory with the ING PDF files",
    )
    # -a, --account
    parser.add_argument(
        "-a",
        "--account",
        type=str,
        required=False,
        default="giro",
        help="Account type to parse if directory is specified e.g. Giro, Extra (Default: Giro)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default="ing_kontoauszug.csv",
        help="Output file (Default: ing_kontoauszug.csv)",
    )
    args = parser.parse_args()

    path = Path(args.path)

    df = []
    if path.is_file() and path.suffix == ".pdf":
        # Checking account statement
        if 'kontoauszug' in path.name.lower():
            df = parse_ing_kontoauszug(Path(args.path))
        # Investment account statement
        if 'depotauszug' in path.name.lower():
            df = parse_ing_depotauszug(Path(args.path))
        # Invoice
        if 'abrechnung' in path.name.lower():
            df = parse_ing_abrechnung(Path(args.path))
        else:
            print(f"{path.name} is not a recognized format!")
    elif path.is_dir():
        for file in path.glob("*.pdf"):
            if ("kontoauszug" in file.name.lower()) and (
                args.account.lower() in file.name.lower()
            ):
                df.append(parse_ing_kontoauszug(file))
        df = pd.concat(df)
    else:
        print(f"Invalid input: {path}", file=stderr)
        exit(1)

    if not df.empty:
        df = df.sort_values("date", ascending=False)
        df.to_csv(args.output, index=False)
    else:
        print("The system was unable to parse the input")