# Retail Analytics: Time Series, Churn, and Recommendation System

## Overview

This project is a comprehensive retail analytics pipeline built to
analyze a retail dataset (Superstore, 9,800+ transactions, 2015--2018).
It provides actionable insights through sales analysis, customer
segmentation, churn analysis, time series forecasting, market basket
analysis, and a hybrid recommendation system. The project is structured
as a modular Python package, includes a FastAPI application for
real-time product recommendations, and supports deployment via Docker.
Key features include:

-   **Sales Analysis**: Analyzes sales trends by category, region,
    segment, and time (day, month, year).
-   **Customer Analysis**: Tracks orders, new vs. repeat customers, and
    customer behavior.
-   **Churn Analysis**: Segments customers into Active, At Risk,
    Churning, and Lost, analyzing churn patterns.
-   **Forecasting**: Uses SARIMA and seasonal decomposition for sales
    predictions and Month-over-Month growth.
-   **Basket Analysis**: Identifies product associations using the
    Apriori algorithm and analyzes basket size trends.
-   **Recommendation System**: Combines market basket analysis and
    collaborative filtering for personalized product suggestions.
-   **FastAPI Application**: Serves recommendations via a RESTful API,
    deployable locally or with Docker.

The project is hosted on GitHub, with unit tests for reliability and
detailed documentation for reproducibility.

## Project Structure
```
    retail_analytics/
    ├── src/                    # Python modules for analysis
    │   ├── data_preprocessing.py
    │   ├── sales_analysis.py
    │   ├── customer_analysis.py
    │   ├── churn_analysis.py
    │   ├── forecasting.py
    │   ├── basket_analysis.py
    │   ├── recommendation.py
    │   ├── visualization.py
    │   ├── utils.py
    ├── api/                    # FastAPI application
    │   ├── main.py
    │   ├── requirements.txt
    ├── data/                   # Dataset storage
    │   ├── raw/
    │   │   └── train.csv      # Superstore dataset (not included)
    ├── notebooks/              # Jupyter notebooks for EDA
    │   ├── exploratory_analysis.ipynb
    │   ├── visualization.ipynb
    ├── tests/                  # Unit tests
    │   ├── test_sales_analysis.py
    │   ├── test_churn_analysis.py
    │   ├── test_forecasting.py
    │   ├── test_basket_analysis.py
    │   ├── test_recommendation.py
    │   ├── test_api.py
    ├── docs/                   # Documentation and visualizations
    │   ├── analysis.md         # Analysis results
    │   ├── visualizations/    # Exported plots
    ├── Dockerfile             # Docker configuration for API
    ├── requirements.txt       # Project dependencies
    ├── main.py                # Entry point for analysis pipeline
    └── README.md              # Project documentation
```
## Recommendation System

The recommendation system is a hybrid model combining **market basket
analysis** (Apriori algorithm) and **collaborative filtering** (cosine
similarity). It provides personalized product suggestions based on user
purchase history, cart contents, or product categories.

### How It Works

-   **Market Basket Analysis**:
    -   Uses the Apriori algorithm to identify frequent itemsets
        (minimum support: 0.001).
    -   Generates association rules with a minimum lift of 1.5, sorted
        by confidence.
    -   Rules are stored as a dictionary for efficient lookup, mapping
        antecedents (items in the cart) to consequents (recommended
        items) with confidence and lift scores.
-   **Collaborative Filtering**:
    -   Builds a customer-item matrix using `TransactionEncoder`.
    -   Computes cosine similarity between customers based on their
        purchase histories.
    -   Recommends items purchased by similar users, weighted by
        similarity scores.
-   **Hybrid Approach**:
    -   For known users (in the dataset), combines collaborative
        filtering (weight `alpha`) and market basket analysis (weight
        `beta`).
    -   `alpha` is 0.7 for users with \>5 items purchased, 0.3 for those
        with ≤5, and 0 for unknown users.
    -   If a cart is provided, recommendations blend items from
        association rules (based on cart subsets) and collaborative
        filtering.
    -   If a category is specified (e.g., "Binders", "Phones"), returns
        top products from that category's popular catalogue.
    -   If no cart or category is provided, uses collaborative filtering
        for known users or falls back to popular products.
-   **Popular Catalogue**:
    -   Maintains a list of the top two products per sub-category (e.g.,
        "Paper", "Chairs") based on purchase frequency.
    -   Ensures recommendations are practical and aligned with
        high-demand items.

The system is accessible via a FastAPI endpoint (`/recommend`), which
accepts a customer name, optional cart, and optional category, returning
up to four recommended products.

## Installation

### Prerequisites

-   Python 3.8+
-   Docker (optional, for API deployment)
-   Git

### Local Setup

1.  Clone the repository:

    ``` bash
    git clone https://github.com/yourusername/retail_analytics.git
    cd retail_analytics
    ```

2.  Install dependencies:

    ``` bash
    pip install -r requirements.txt
    ```

3.  Download the Superstore dataset and place it in
    `data/raw/train.csv`:

    -   \[Link to dataset, e.g., Kaggle Superstore dataset\]
    -   Alternatively, use a sample dataset (`data/raw/sample.csv`) for
        testing.

### Docker Setup

To run the FastAPI application using Docker: 1. Ensure Docker is
installed and running. 2. Build the Docker image:
`bash    docker build -t retail-analytics-api .` 3. Run the container:
`bash    docker run -p 8000:8000 retail-analytics-api` 4. Access the API
at `http://localhost:8000/docs`.

> **Note**: The `Dockerfile` assumes the dataset (`train.csv`) is
> included in `data/raw/`. If using a large dataset, modify the
> `Dockerfile` to download it during the build or mount a volume.

## Usage

### Run the Analysis Pipeline

Execute the full analysis pipeline (sales, churn, forecasting, basket
analysis, recommendations):

``` bash
python main.py
```

This generates visualizations in `docs/visualizations/` and prints key
results to the console.

### Run the FastAPI Application

Start the recommendation API locally:

``` bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Access the API at `http://localhost:8000/docs` to test the `/recommend`
endpoint interactively.

**Example API Request**:

``` bash
curl -X POST "http://localhost:8000/recommend" \
-H "Content-Type: application/json" \
-d '{"customer_name": "Micky", "cart": ["Paper"], "category": null}'
```

**Response**:

``` json
{
  "recommendations": ["Avery Non-Stick Binders", "Easy-staple paper"]
}
```

**Supported Categories and Cart Items**: - Paper, Binders, Storage, Labels, Art,
Phones, Chairs, Fasteners, Furnishings, Accessories, Envelopes,
Bookcases, Appliances, Tables, Supplies, Machines, Copiers

### Run Tests

Run unit tests to verify the recommendation system and API:

``` bash
pytest tests/
```

This executes tests in `tests/` for all modules, including
`test_recommendation.py`.

## API Documentation

The FastAPI application provides a Swagger UI at
`http://localhost:8000/docs` for testing the `/recommend` endpoint. The
endpoint accepts: - `customer_name` (str): Name of the customer (e.g.,
"Micky"). - `cart` (list\[str\], optional): List of products in the cart
(e.g., \["Paper", "Binders"\]). - `category` (str, optional): Product
category for recommendations (e.g., "Phones").

The response returns a JSON object with a `recommendations` key
containing a list of up to four product names.

## Contact

-   **Author**: Sraban Mondal
-   **Email**: srabanmondal1@gmail.com

## License

This project is licensed under the MIT License.
