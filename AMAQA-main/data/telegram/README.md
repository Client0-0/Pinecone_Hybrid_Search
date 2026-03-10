## Data Structure
The dataset is splitted in multiple jsonl files, each containing a portion of the data. The files are named in the format `data_part_X.jsonl`, where `X` is a number indicating the part of the dataset.

Each `.jsonl` file contains multiple entries in the following format:

```json
{
  "text": "This is the text of the message",
  "id": 123456789,
  "metadata": {
    "date": "2024-07-28 00:00:00",
    "is_forwarded": false,
    "has_media": false,
    "was_edited": false,
    "reactions": "reactions": {
      "_": "MessageReactions",
      "reactions": [
        {
          "_": "Reaction",
          "emoji": "💯",
          "count": 2
        }
      ]
    },
    "reactions_count": 2,
    "chat_name": "This is the name of the group chat"
  },
  "ground_truth": {
    "toxicity": 0.013005874,
    "profanity": 0.013268576,
    "insult": 0.008044879,
    "identity_attack": 0.0029968263,
    "threat": 0.007029374,
    "emotion": "neutral",
    "topics": ["Topic1", "Topic2"]
  }
}
```

### Fields Description
- **text**: The message content.
- **id**: Unique identifier for the message. It's an incremental integer starting from 1. It has nothing in common with the original Telegram message ID, and it is only used for indexing purposes in this dataset.
- **metadata**:
  - `date`: Timestamp of the message.
  - `is_forwarded`: Boolean indicating if the message was forwarded.
  - `has_media`: Boolean indicating if the message contains media.
  - `was_edited`: Boolean indicating if the message was edited.
  - `reactions`: Contains a list of reactions to the message (if available), where each reaction includes: the emoji used for the reaction and the number of times this reaction was added.
  - `reactions_count`: Total count of reactions.
  - `chat_name`: Name of the chat where the message was posted.
- **ground_truth**:
  - `toxicity`: The probability that the content is considered toxic. Score provided by [Perspective API](https://perspectiveapi.com/).
  - `profanity`: The probability that the content contains profanity. Score provided by Perspective API.
  - `insult`: The probability that the content contains an insult. Score provided by Perspective API.
  - `identity_attack`: The probability that the content includes an identity attack. Score provided by Perspective API.
  - `threat`: The probability that the content is a threat. Score provided by Perspective API.
  - `emotion`: Emotion conveyed by the text.
  - `topics`: List of topics (if any).
