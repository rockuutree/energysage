# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional
import logging

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

# Load and process data
def load_data():
    df = pd.read_csv('solar.csv')
    # Clean data
    df = df.replace('', np.nan)
    df['p_cap_ac'] = pd.to_numeric(df['p_cap_ac'], errors='coerce')
    df['p_cap_dc'] = pd.to_numeric(df['p_cap_dc'], errors='coerce')
    df['p_year'] = pd.to_numeric(df['p_year'], errors='coerce')
    return df

df = load_data()
print(f"Loaded {len(df)} installations")
print("Available states:", sorted(df['p_state'].unique().tolist()))

@app.get("/api/state/{state}")
async def get_state_data(state: str):
    """Get detailed data for a specific state"""
    print(f"Fetching data for state: {state}")
    state_data = df[df['p_state'] == state].copy()
    
    if len(state_data) == 0:
        return {"error": "No installations found for this state"}
    
    installations = []
    for _, row in state_data.iterrows():
        installation = {
            "case_id": row['case_id'],
            "name": row['p_name'] if pd.notna(row['p_name']) else None,
            "county": row['p_county'],
            "latitude": float(row['ylat']),
            "longitude": float(row['xlong']),
            "capacity_ac": float(row['p_cap_ac']) if pd.notna(row['p_cap_ac']) else None,
            "capacity_dc": float(row['p_cap_dc']) if pd.notna(row['p_cap_dc']) else None,
            "year": int(row['p_year']) if pd.notna(row['p_year']) else None,
            "technology": row['p_tech_pri'] if pd.notna(row['p_tech_pri']) else None,
            "axis_type": row['p_axis'] if pd.notna(row['p_axis']) else None,
            "has_battery": "batteries" in str(row['p_battery']).lower() if pd.notna(row['p_battery']) else False
        }
        installations.append(installation)
    
    stats = {
        "totalInstallations": len(state_data),
        "totalCapacity": float(state_data['p_cap_ac'].sum()),
        "averageCapacity": float(state_data['p_cap_ac'].mean()),
        "totalCounties": len(state_data['p_county'].unique()),
        "yearRange": [
            int(state_data['p_year'].min()),
            int(state_data['p_year'].max())
        ] if not state_data['p_year'].isna().all() else None
    }
    
    return {
        "stats": stats,
        "installations": sorted(installations, key=lambda x: x['year'] if x['year'] else 0, reverse=True)
    }

@app.get("/api/states")
async def get_states():
    """Get list of all states with installations"""
    states = sorted(df['p_state'].unique().tolist())
    state_counts = df.groupby('p_state').size().to_dict()
    state_capacities = df.groupby('p_state')['p_cap_ac'].sum().to_dict()
    
    state_info = [
        {
            "code": state,
            "installations": state_counts.get(state, 0),
            "totalCapacity": float(state_capacities.get(state, 0))
        }
        for state in states
    ]
    
    return {"states": state_info}