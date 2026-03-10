# AMAQA: A Metadata-based QA Dataset for RAG Systems

## Overview

AMAQA is a high-quality, metadata-enriched Question-Answer dataset designed for Retrieval-Augmented Generation (RAG) systems. It includes about 1.1 million English messages collected from 26 public Telegram groups, enriched with metadata such as timestamps and chat names. It also contains 20,000 hotel reviews with metadata. In addition, the dataset provides 2600 high-quality QA pairs built across both domains — Telegram messages and hotel reviews — making AMAQA a valuable resource for advancing research on metadata-driven QA and RAG systems.

---

## Repository Structure

```
data/
│
├── telegram/
│   ├── *.jsonl
│   └── README.md
│
└── hotel_reviews/
    └── hotel_reviews.csv
    └── README.md

benchmark/
│
├── qa_hotel_reviews.csv
├── qa_hotel_reviews_meta.csv
├── qa_telegram.csv
└── qa_telegram_meta.csv
```

### `data/`

Contains the full dataset divided by domain:

* **`telegram/`**

  * Contains Telegram messages stored as `.jsonl` files.
  * Each `.jsonl` file contains one JSON object per line.
  * Includes a `README.md` file describing the JSON files.

* **`hotel_reviews/`**

  * Contains hotel reviews stored as `.csv` file.
  * Includes a `README.md` file describing the CSV schema.


> ⚠️ Note: The detailed description of the JSON structures are provided in `data/telegram/DATA_STRUCTURE.md` and `data/hotel_reviews/DATA_STRUCTURE.md`.

---

## Benchmark Folder

The `benchmark/` folder contains the Question-Answer pairs used for evaluation.

### Files

* `qa_hotel_reviews.csv`
* `qa_hotel_reviews_meta.csv`
* `qa_telegram.csv`
* `qa_telegram_meta.csv`

Each CSV file contains the following columns:

| Column         | Description                                                         |
| -------------- | ------------------------------------------------------------------- |
| `question`     | The natural language question.                                      |
| `answer`       | The ground-truth answer.                                            |
| `relevant_doc` | The full text of the document from which the answer can be derived. |
| `doc_id`       | The unique identifier of the relevant document within the dataset.  |

### Answer within text or within metadata

* Files **without** `_meta` in the name:

  * The answer is contained in the **text** of the relevant document.

* Files **with** `_meta` in the name:

  * The answer is found in the **metadata** of the relevant document rather than in the main text.

---

## Prompts

* `prompts.txt`
  Contains the prompts used for topic extraction tasks and QA creation.

### Warning:

> ⚠️ The prompts used during dataset construction may contain potentially offensive or defamatory terms. These were necessary to induce the generation of toxic or controversial content reflective of real-world Telegram discussions.

---

## Ethical Considerations

The data collection was conducted with care to include only information from public Telegram channels and groups, explicitly excluding personal data such as usernames, phone numbers, user IDs, and chat IDs. The process aligns with Telegram’s Terms of Service and Telegram API’s Terms of Service, as neither prohibits the collection of public chat data.

Our research complies with the academic research exemptions outlined in Article 85 of the GDPR, which provide flexibility for processing publicly available data in the interest of freedom of expression and academic purposes.

We follow the GDPR’s principle of data minimization by focusing solely on English textual content from public posts. However, as the dataset includes channels discussing controversial topics, it may contain controversial or sensitive messages.

---

## Citation

If you use AMAQA in your research, please cite:

```bibtex
@misc{bruni2026amaqametadatabasedqadataset,
      title={AMAQA: A Metadata-based QA Dataset for RAG Systems}, 
      author={Davide Bruni and Marco Avvenuti and Nicola Tonellotto and Maurizio Tesconi},
      year={2026},
      eprint={2505.13557},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2505.13557}, 
}
```

---

## License

This project is licensed under the [CC BY-NC-ND 4.0](http://creativecommons.org/licenses/by-nc-nd/4.0/) license.

[![License: CC BY-NC-ND 4.0](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-nd/4.0/)

---
