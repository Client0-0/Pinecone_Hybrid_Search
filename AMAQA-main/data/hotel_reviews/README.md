# Hotel Reviews with Emotions (Clean)

This document describes the fields in `hotel_reviews_with_emotions_clean.csv` and what they represent.

## Fields

- `address`: Hotel street address.
- `city`: Hotel city.
- `latitude`: Hotel latitude in decimal degrees.
- `longitude`: Hotel longitude in decimal degrees.
- `name`: Hotel name.
- `postalCode`: Hotel postal/ZIP code.
- `province`: Hotel state/province code.
- `reviews.date`: Review date in ISO 8601 format (UTC).
- `reviews.rating`: Review rating as a numeric score.
- `reviews.text`: Full review text.
- `reviews.title`: Review title or short summary. 
  
  (Before embedding calculation, during the indexing phase, it's combined with `reviews.text` to create the final review content for retrieval.)
- `reviews.userCity`: Reviewer's city (when available).
- `reviews.userProvince`: Reviewer's state/province (when available).
- `emotion`: Detected emotion label for the review text (e.g., joy, sadness, anger, fear, surprise).
