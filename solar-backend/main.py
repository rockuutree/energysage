"""
Solar Installations API
Uses FastAPI to create a simple API for solar installation data.
Provides endpoints for state-specific and nationwide installation data.

The U.S. Large-Scale Solar Photovoltaic Database
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Frontend development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and process data

    # Load and preprocess solar installation data from CSV file.
    
    # Returns:
    #     pd.DataFrame: Cleaned DataFrame containing solar installation data
        
    # Processing steps:
    # 1. Load CSV file
    # 2. Replace empty strings with NaN
    # 3. Convert numeric columns to proper data types

def load_data():
    # Loading in data from CSV using pandas
    df = pd.read_csv('solar.csv')
    # Clean data
    df = df.replace('', np.nan)
    # Convert columns to numeric, and convert empty values to NaN
    df['p_cap_ac'] = pd.to_numeric(df['p_cap_ac'], errors='coerce')
    df['p_cap_dc'] = pd.to_numeric(df['p_cap_dc'], errors='coerce')
    df['p_year'] = pd.to_numeric(df['p_year'], errors='coerce')
    return df

# Load data on startup
df = load_data()
print(f"Loaded {len(df)} installations")
print("Available states:", sorted(df['p_state'].unique().tolist()))


    # """
    # Get detailed solar installation data for a specific state.
    
    # Args:
    #     state (str): Two-letter state code (e.g., 'CA', 'NY')
        
    # Returns:
    #     dict: Dictionary containing:
    #         - stats: State-level statistics including total installations,
    #                 capacities, and year range
    #         - installations: List of individual installation details
            
    # Error returns:
    #     dict: Error message if no installations found for state
    # """
@app.get("/api/state/{state}")
async def get_state_data(state: str):
    # Get detailed data for a specific stat
    print(f"Fetching data for state: {state}")
    # Filter data for the specific state
    state_data = df[df['p_state'] == state].copy()
    
    # Empty dataset for x state
    if len(state_data) == 0:
        return {"error": "No installations found for this state"}
    
    # Process Individual Installations
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
    
    # Calculate State statistics
    stats = {
        # Count Installations
        "totalInstallations": len(state_data),
        # Sum AC Capacity
        "totalCapacity": float(state_data['p_cap_ac'].sum()),
        # Average AC Capacity
        "averageCapacity": float(state_data['p_cap_ac'].mean()),
        # Count unique counties
        "totalCounties": len(state_data['p_county'].unique()),
        # Installation year range
        "yearRange": [
            int(state_data['p_year'].min()),
            int(state_data['p_year'].max())
        ] if not state_data['p_year'].isna().all() else None
    }
    
    # 
    return {
        "stats": stats,
        "installations": sorted(installations, key=lambda x: x['year'] if x['year'] else 0, reverse=True)
    }


    """
    Get summary information for all states with solar installations.
    
    Returns:
        dict: Dictionary containing list of states with:
            - code: State code
            - installations: Number of installations
            - totalCapacity: Total AC capacity in MW
    """
    
@app.get("/api/states")
async def get_states():
    """Get list of all states with installations"""
    states = sorted(df['p_state'].unique().tolist())
    # Calculate installations per state
    state_counts = df.groupby('p_state').size().to_dict()
    # Calculate total capacity per state
    state_capacities = df.groupby('p_state')['p_cap_ac'].sum().to_dict()
    
    # Combine State information
    state_info = [
        {
            "code": state,
            "installations": state_counts.get(state, 0),
            "totalCapacity": float(state_capacities.get(state, 0))
        }
        for state in states
    ]
    
    return {"states": state_info}