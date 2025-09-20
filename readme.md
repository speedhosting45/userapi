# 🌍 Random Address Generator API

A FastAPI-based service that generates completely random  worldwide addresses, 
including names, phone numbers, and geolocation.

## Features
- realistic names (first/last)
- Random street, city, state, country
- Country-specific postal code formats
- Country-specific phone number formats
- Random latitude/longitude
- Multiple addresses with `?count=N`

## Endpoints
- `/` → API info
- `/address` → Get a single random address
- `/addresses?count=10` → Get multiple random addresses
- `/countries` → List supported countries

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
