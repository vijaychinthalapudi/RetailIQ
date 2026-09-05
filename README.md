TRACK_ID=PS03

# RetailIQ

# AI-Powered Sales and Inventory Copilot for Small Retail Businesses

RetailIQ is an AI-powered sales and inventory copilot designed to help small retail business managers make faster, evidence-based decisions from their sales, inventory, product, and store data.

Instead of requiring a manager to manually inspect reports and stock sheets, RetailIQ allows questions to be asked in natural language and returns concise answers supported by the application's underlying business data.

The system focuses on three important retail situations:

- Products that are likely to run out soon
- Inventory that is not moving
- Sales spikes or drops that deserve attention

RetailIQ also provides recommended actions and the underlying business evidence used to support those recommendations.


## Problem

Retail managers often have useful information spread across sales reports, inventory records, product information, and store data, but making decisions from those sources can be time-consuming.

RetailIQ addresses this problem by combining deterministic business analytics with a grounded GenAI copilot.

The system is designed around the principle:

> **The data is the source of truth; AI explains the data rather than inventing business facts.**

## Key Features

### 1. Sales Dashboard

RetailIQ provides an overview of sales performance using the available sales data.

The dashboard exposes metrics such as:

- Total units sold
- Revenue
- Critical inventory situations
- Sales spikes

The metrics are calculated from the application's underlying sales and inventory data.


### 2. Inventory Risk Detection

RetailIQ analyzes inventory information and identifies products that require attention.

The application can highlight:

- Critical stock situations
- Products likely to experience stock-outs
- Inventory that is not moving
- Products requiring inventory review

Recommendations are generated from deterministic business logic and are presented separately from the AI-generated summary.


### 3. Sales Trend Analysis

RetailIQ analyzes sales trends and identifies significant changes in sales behaviour.

The system can identify situations such as:

- Sales spikes
- Sales drops
- Products with strong sales performance
- Products requiring closer review


### 4. Natural-Language Copilot

Managers can ask questions in plain language rather than manually navigating reports.

Example questions include:

What products are likely to run out soon?

Which products are overstocked?

How did a product perform this month?

Which products need attention today?

What are the major sales trends?

# 5. Evidence-Grounded Answers

RetailIQ separates deterministic business calculations from language-model reasoning.

The deterministic analytics layer is responsible for:

- Numerical calculations
- Sales metrics
- Inventory status
- Trends
- Recommendations
- Business evidence

Gemini is used to produce a concise natural-language summary from the supplied evidence.

The application instructs the model to:

- Never invent numbers or business facts
- Use the supplied business evidence as the source of truth
- Avoid contradicting the evidence
- State when the available data is insufficient
- Avoid making definite stock-out claims
- Support recommendations with available evidence

This keeps the AI layer focused on explanation and reasoning while deterministic logic remains responsible for the underlying business facts.

# Technology Stack

## Backend

- Python
- Flask
- Pandas
- NumPy

## Frontend

- HTML
- CSS
- JavaScript

# GenAI

- Google Gemini API
- Gemini generative model for manager-facing summaries
- gemini-embedding-001 for evidence embeddings

## Retrieval

- Local embedding generation
- Local saved embedding index
- NumPy-based vector processing
- Application-owned evidence retrieval
- No hosted vector database is required.

# Project Structure

RetailIQ/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── evidence_documents.json
│   ├── evidence_embeddings.npy
│   ├── inventory.csv
│   ├── products.csv
│   ├── sales.csv
│   └── stores.csv
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── src/
│   ├── analytics.py
│   ├── business_rules.py
│   ├── context_builder.py
│   ├── data_loader.py
│   ├── embedding_client.py
│   ├── evidence_builder.py
│   ├── gemini_client.py
│   ├── index_manager.py
│   ├── query_router.py
│   ├── retriever.py
│   ├── test_business_rules.py
│   └── test_gemini.py
│
├── build_index.py
├── generate_data.py
│
├── test_context_builder.py
├── test_embeddings.py
├── test_retriever.py
└── test_saved_index.py

## Data

RetailIQ uses its own generated retail data and evidence documents.

The repository contains:

## products.csv

- Product-level information used by the application.

## stores.csv

- Store information used by the retail analytics system.

## sales.csv

- Sales records used to calculate sales metrics, revenue, product performance, and trends.

## inventory.csv

- Inventory information used to identify products requiring attention.

## evidence_documents.json

- Business evidence documents used by the evidence retrieval pipeline.

## evidence_embeddings.npy

- Saved embedding vectors used by the local retrieval system.


The generated data and saved retrieval artifacts are included in the repository so that the application does not require a separate data-generation or indexing command during normal execution.

# How the Copilot Works

A manager question follows this general pipeline:

Manager Question
       │
       ▼
Intent Detection
       │
       ▼
Evidence Retrieval
       │
       ▼
Grounded Context
       │
       ▼
Gemini Reasoning
       │
       ▼
Concise Manager Summary
       │
       ├───────────────┐
       ▼               ▼
Deterministic       Business
Evidence            Cards


# Grounding and Reliability

RetailIQ follows a strict grounding approach.

The application treats deterministic business calculations as the source of truth for:

- Numbers
- Dates
- Inventory status
- Trends
- Recommendations

The AI layer is instructed not to invent business information.

When the available evidence is insufficient to answer a question, the system is designed to state that the available data is insufficient rather than guessing.

For stock-out situations, the system avoids presenting uncertain predictions as guaranteed outcomes.

## How to Run

### Requirements

- Python 3.11
- Gemini API key

### Install Dependencies

```bash
pip install -r requirements.txt

python app.py

http://localhost:8000

## Data and Documents

RetailIQ uses generated retail data for:

- Products
- Stores
- Sales
- Inventory

The repository also contains generated evidence documents and precomputed embeddings used by the application.


## Demo Video

[▶️ Watch the Demo Video](https://drive.google.com/file/d/1kTiCmPU3EXzUWhawqNYrK8VcuU0QuRED/view?usp=sharing)

## GitHub Repository

[📂 RetailIQ GitHub Repository](https://github.com/vijaychinthalapudi/RetailIQ)

