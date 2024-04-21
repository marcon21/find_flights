from ryanair import Ryanair
from datetime import datetime, timedelta
import argparse
from colorama import Fore, Back, Style
import streamlit as st
import airportsdata
import pandas as pd

api = Ryanair("EUR")
airports_a = airportsdata.load("IATA")
airports_b = airportsdata.load("IATA")


def switch_airports():
    st.session_state["airport_a"], st.session_state["airport_b"] = (
        st.session_state["airport_b"],
        st.session_state["airport_a"],
    )


def clear_airports():
    st.session_state.pop("airport_a")
    st.session_state.pop("airport_b")


if "airport_a" not in st.session_state:
    st.session_state["airport_a"] = ["BGY", "BLQ", "VCE", "VRN"]
    st.session_state["airport_b"] = ["EIN", "CGN", "CRL"]


airports_a_selected = st.multiselect(
    "Select starting airports",
    list(airports_a.keys()),
    format_func=lambda x: airports_a[x]["name"],
    default=st.session_state["airport_a"],
    label_visibility="visible",
    # key="a",
)


airports_b_selected = st.multiselect(
    "Select ending airports",
    list(airports_b.keys()),
    format_func=lambda x: airports_b[x]["name"],
    default=st.session_state["airport_b"],
    label_visibility="visible",
    key="b",
)

st.write("Switch starting and ending airports:")
switch = st.button("Switch", on_click=switch_airports)
st.write(
    'Reset all selections to defaults (["BGY", "BLQ", "VCE", "VRN"] --> ["EIN", "CGN", "CRL"]):'
)
reset = st.button("Reset", on_click=lambda: st.session_state.clear())
st.write("Clear airport selections:")
clear = st.button("Clear", on_click=clear_airports)

st.divider()


start = f"Selected starting airports: {', '.join([airports_a[x]['iata'] for x in airports_a_selected])}"
st.markdown(start)
end = f"Selected destination airports: {', '.join([airports_b[x]['iata'] for x in airports_b_selected])}"
st.markdown(end)


# end_airport = st.multiselect("Select airports", list(airports.keys()))
start_date = st.date_input("Select start date", datetime.now().date())
end_date = st.date_input("Select end date", datetime.now().date() + timedelta(days=3))
delta_days = (end_date - start_date).days
st.write(f"Selected date range: {start_date} to {end_date}")

search = st.button(
    "Search",
    on_click=lambda: find_flights(
        [airports_a[x]["iata"] for x in airports_a_selected],
        [airports_b[x]["iata"] for x in airports_b_selected],
        start_date,
        delta_days,
    ),
)


def find_flights(start, end, start_date, delta_days):
    possible_flights = []
    for d in range(0, delta_days):
        for s in start:
            for e in end:
                flights = api.get_cheapest_flights(
                    airport=s,
                    date_from=start_date + timedelta(days=d),
                    date_to=start_date + timedelta(days=d),
                    departure_time_from="08:00",
                    departure_time_to="23:00",
                    destination_airport=e,
                )
                if flights:

                    possible_flights.append(flights[0])
                else:
                    continue
                    # print(f"No flights from {s} to {e}")

    ordered_flights = sorted(possible_flights, key=lambda x: x.price)
    pd_flights = pd.DataFrame(
        [
            {
                "origin": f.origin,
                "destination": f.destination,
                "price (€)": int(f.price),
                "departureTime": f.departureTime,
            }
            for f in ordered_flights
        ]
    )

    st.dataframe(
        pd_flights.style.background_gradient(
            axis=0,
            cmap="RdYlGn_r",
        ),
        use_container_width=True,
        # hide_index=True,
    )
