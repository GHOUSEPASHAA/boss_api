from fastapi import FastAPI
from faker import Faker
import random
import hashlib
from datetime import datetime, timedelta
import requests
import uuid
import uvicorn
import json

app = FastAPI(title="BOSS Beverage API")

fake = Faker()

properties = {
    "RLC": "Red Lantern Casino",
    "BMC": "Blue Meridian Casino",
    "GPC": "Glass Palm Casino"
}

beverages = [
    {
        "boss_beverage_description": "our classic strawberry puree with rum",
        "boss_beverage_id": 133,
        "boss_beverage_name": "Strawberry Daquri",
        "boss_beverage_type": "Cocktail"
    },
    {
        "boss_beverage_description": "fresh lime margarita with tequila",
        "boss_beverage_id": 144,
        "boss_beverage_name": "Classic Margarita",
        "boss_beverage_type": "Cocktail"
    },
    {
        "boss_beverage_description": "premium whiskey with ice",
        "boss_beverage_id": 155,
        "boss_beverage_name": "Whiskey On Rocks",
        "boss_beverage_type": "Whiskey"
    },
    {
        "boss_beverage_description": "sparkling mojito with mint",
        "boss_beverage_id": 166,
        "boss_beverage_name": "Mint Mojito",
        "boss_beverage_type": "Mocktail"
    }
]


def generate_person_id(activeclubid):

    return str(
        int(
            hashlib.md5(
                ("BOSS" + activeclubid).encode()
            ).hexdigest(),
            16
        ) % 90000 + 10000
    )


def generate_beverage_json():

    beverage_count = random.randint(1, 3)

    beverage_list = []

    for _ in range(beverage_count):

        beverage = random.choice(
            beverages
        )

        revenue = round(
            random.uniform(5, 25),
            2
        )

        beverage_list.append({

            "boss_beverage_description":
                beverage[
                    "boss_beverage_description"
                ],

            "boss_beverage_id":
                beverage[
                    "boss_beverage_id"
                ],

            "boss_beverage_name":
                beverage[
                    "boss_beverage_name"
                ],

            "boss_beverage_type":
                beverage[
                    "boss_beverage_type"
                ],

            "boss_cash_value":
                0,

            "boss_is_free_prize":
                random.choice(
                    [True, False]
                ),

            "boss_order_beverage_id":
                random.randint(
                    3000000,
                    4000000
                ),

            "boss_partner_system_cash_value":
                revenue,

            "boss_revenue":
                revenue
        })

    return beverage_list


def generate_base_boss_order(activeclubid):

    person_id = generate_person_id(
        activeclubid
    )

    property_code = random.choice(
        list(properties.keys())
    )

    property_name = properties[
        property_code
    ]

    order_timestamp = (
        datetime.now()
        - timedelta(
            days=random.randint(1, 30),
            hours=random.randint(1, 12)
        )
    )

    beverage_details = (
        generate_beverage_json()
    )

    details = ", ".join([
    item["boss_beverage_name"]
    for item in beverage_details
    ])

    total_amount = round(
        sum(
            item["boss_revenue"]
            for item in beverage_details
        ),
        2
    )

    return {

        "EVENT_TIMESTAMP":
            order_timestamp.isoformat(),

        "EVENT_TIMESTAMP_PROPERTY":
            order_timestamp.isoformat(),

        "EVENT_TIMESTAMP_PROPERTY_TIMEZONE":
            "America/New_York",

        "DURATION":
            random.randint(5, 60),

        "GAMING_DATE":
            order_timestamp.date().isoformat(),

        "GAMING_DATE_TIMEZONE":
            "America/New_York",

        "SOURCE_PERSON_KEY":
            hashlib.md5(
        ("BOSS" + activeclubid).encode()
        ).hexdigest(),

        "PERSON_ID":
            person_id,

        "ACTIVE_CLUB_ID":
            activeclubid,

        "SOURCE":
            "BOSS_SYSTEM",

        "ENTITY":
            "BEVERAGE",

        "ACTION":
            "ORDER",

        "ENTITY_ACTION":
            "BEVERAGE:ORDER",

        "DETAILS":
            details,

        "EVENT_ID":
            hashlib.md5(
                str(uuid.uuid4()).encode()
            ).hexdigest(),

        "EVENT_GROUP_ID":
            hashlib.md5(
                activeclubid.encode()
            ).hexdigest(),

        "PROPERTY_NAME":
            property_name,

        "PROPERTY_CODE":
            property_code,

        "PROPERTY_ACCOUNTING_CODE":
            property_code,

        "SF_PROPERTY_ID":
            property_code,

        "PROPERTY_ID":
            property_code,

        "PROPERTY_ADDR1":
            fake.street_address(),

        "PROPERTY_ADDR2":
            fake.secondary_address(),

        "PROPERTY_CITY":
            fake.city(),

        "PROPERTY_STATE":
            fake.state(),

        "PROPERTY_COUNTRY":
            "USA",

        "PROPERTY_POSTAL_CODE":
            fake.postcode(),

        "TRANSACTION_AMOUNT":
            total_amount,

        "PLAYER_VALUE":
            round(
                total_amount * random.uniform(0.1, 0.4),
                2
            ),

        "BOSS_ORDER_ID":
            random.randint(
                100000,
                999999
            ),

        "BOSS_ORDER_CREATED_MACHINE_STAND":
            random.choice([
                "BAR-01",
                "BAR-02",
                "VIP-LOUNGE",
                "POOL-BAR",
                "CASINO-FLOOR"
            ]),

        "BOSS_BAR_ID":
            random.randint(
                1,
                20
            ),

        "BOSS_GUEST_FIRST_NAME":
            fake.first_name(),

        "BOSS_GUEST_LAST_NAME":
            fake.last_name(),

        "BOSS_BEVERAGE_DETAILS":
            beverage_details,

        "LOAD_TIMESTAMP":
            datetime.now().isoformat()
    }


@app.get("/v1/boss-beverage")
async def boss_beverage():

    api_url = (
        "https://casino-api-ob26.onrender.com/"
        "v1/player-activity"
    )

    response = requests.get(
        api_url
    )

    player_data = response.json()

    unique_activeclubids = []

    seen = set()

    for row in player_data:

        activeclubid = row[
            "ACTIVECLUBID"
        ]

        if activeclubid not in seen:

            seen.add(
                activeclubid
            )

            unique_activeclubids.append(
                activeclubid
            )

        if len(unique_activeclubids) == 50:
            break

    final_records = []

    for activeclubid in unique_activeclubids:

        final_records.append(
            generate_base_boss_order(
                activeclubid
            )
        )

    return final_records


if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004
    )
