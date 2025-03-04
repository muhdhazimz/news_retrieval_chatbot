# AI-Powered News Retrieval Chatbot

## Overview

This project involves the development of an advanced AI-powered assistant designed to enhance knowledge retrieval for enterprise users. The assistant retrieves and answers user queries based on two primary sources:

1. **Internal Knowledge Base**: The assistant uses a dataset containing news articles and categorized content for answering questions through **Retrieval-Augmented Generation (RAG)**.
2. **Web Search**: When the internal knowledge base does not provide a sufficient answer, the assistant uses a real-time search engine API to fetch relevant data from the web.

The goal of the assistant is to provide accurate, real-time information to enterprise users, streamlining knowledge retrieval.

## Features

- **Internal Knowledge Base Integration**: The assistant uses a dataset containing news articles and their categories as its internal knowledge base.
- **Web Search Integration**: If the internal knowledge base does not have a relevant answer, the assistant performs a web search using the **Serper API** to fetch real-time data.
- **AI-Enhanced Responses**: The assistant leverages AI models (Cohere) to process user queries and retrieve relevant answers.
- **Customizable**: You can easily extend or customize the chatbot to include additional data sources or enhance its capabilities.
- **User-Friendly Interface**: The chatbot interface allows users to ask questions, view past interactions, and get updated responses.

## Requirements

1. **Python**: This project is built using Python.
2. **Environment Variables**: Set up the necessary environment variables to allow API communication and model usage.
3. **Dependencies**: Install the required dependencies from the `requirements.txt`.

## Setup Instructions

### 1. Create `.env` File

Before running the project, you'll need to create a `.env` file in the root directory and populate it with the following variables:

```plaintext
COHERE_API_KEY=your_cohere_api_key
COHERE_MODEL="your_cohere_model_id"
CHATBOT_TEMPERATURE=your_desired_temperature_value
SERPER_API_KEY=your_serper_api_key
EXCEL_TABLE_PATH_LIST="['path_to_your_sample_data.csv']" # multiple files can be added
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the backend code.

```bash
python main.py
```

### 4. Run the frontend code.

Open the `index.html` file.


## Test cases

Below are some example questions that can be asked to test the functionality:

1. What is new on Forex category?
2. Tell me the news on Corporate News category?