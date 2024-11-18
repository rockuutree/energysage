# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_nan_values(obj):
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(v) for v in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj

# Load and process data
def load_data():
    try:
        logger.info("Loading solar.csv...")
        data = pd.read_csv('solar.csv')
        
        # Replace empty strings with NaN
        data = data.replace('', np.nan)
        
        # Convert specific columns to appropriate types
        data['p_img_date'] = pd.to_datetime(data['p_img_date'], format='%Y%m%d', errors='coerce')
        data['p_year'] = pd.to_numeric(data['p_year'], errors='coerce')
        data['p_cap_ac'] = pd.to_numeric(data['p_cap_ac'], errors='coerce')
        data['p_cap_dc'] = pd.to_numeric(data['p_cap_dc'], errors='coerce')
        data['p_area'] = pd.to_numeric(data['p_area'], errors='coerce')
        
        logger.info(f"Successfully loaded {len(data)} records")
        return data
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        return pd.DataFrame()

df = load_data()

@app.get("/")
async def root():
    return {"message": "Solar Installations API"}

@app.get("/installations")
async def get_installations(
    state: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = Query(50, le=1000),
    offset: int = 0
):
    try:
        filtered_df = df.copy()
        
        if state:
            filtered_df = filtered_df[filtered_df['p_state'] == state]
        if year:
            filtered_df = filtered_df[filtered_df['p_year'] == year]
        
        total = len(filtered_df)
        
        # Convert selected records to dict and clean NaN values
        records = filtered_df.iloc[offset:offset + limit].replace({np.nan: None}).to_dict('records')
        
        # Clean any remaining NaN values
        cleaned_records = clean_nan_values(records)
        
        return {
            "total": total,
            "installations": cleaned_records
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": str(e)}

@app.get("/states")
async def get_states():
    try:
        states = sorted(df['p_state'].dropna().unique().tolist())
        return {"states": states}
    except Exception as e:
        logger.error(f"Error getting states: {str(e)}")
        return {"error": str(e)}

@app.get("/stats")
async def get_stats():
    try:
        return {
            "total_installations": len(df),
            "total_capacity_ac": float(df['p_cap_ac'].sum()) if not np.isnan(df['p_cap_ac'].sum()) else 0,
            "average_size": float(df['p_cap_ac'].mean()) if not np.isnan(df['p_cap_ac'].mean()) else 0,
            "states_count": len(df['p_state'].unique()),
            "year_range": [
                int(df['p_year'].min()) if not np.isnan(df['p_year'].min()) else None,
                int(df['p_year'].max()) if not np.isnan(df['p_year'].max()) else None
            ]
        }
    except Exception as e:
        logger.error(f"Error calculating stats: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)