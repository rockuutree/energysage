# solar/import_solar_data.py

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Set up Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar.settings')
django.setup()

from solar.models import SolarInstallation

def import_solar_data():
    csv_path = os.path.join(current_dir, 'solar.csv')
    success_count = 0
    error_count = 0
    
    print(f"Reading CSV from: {csv_path}")
    
    try:
        # Read only the columns we need
        columns = ['case_id', 'p_state', 'p_county', 'ylat', 'xlong', 
                  'p_name', 'p_year', 'p_cap_ac', 'p_cap_dc', 
                  'p_tech_pri', 'p_area']
        
        df = pd.read_csv(csv_path, usecols=columns)
        print(f"\nFound {len(df)} records to import")
        
        # Bulk create preparation
        installations = []
        
        for index, row in df.iterrows():
            try:
                installation = SolarInstallation(
                    case_id=int(row['case_id']),
                    state=row['p_state'],
                    county=row['p_county'],
                    latitude=float(row['ylat']),
                    longitude=float(row['xlong']),
                    name=str(row['p_name']),
                    year=int(row['p_year']),
                    capacity_ac=float(row['p_cap_ac']),
                    capacity_dc=float(row['p_cap_dc']),
                    tech_primary=str(row['p_tech_pri']),
                    area=float(row['p_area'])
                )
                installations.append(installation)
                success_count += 1
                
                # Batch create every 1000 records
                if len(installations) >= 1000:
                    SolarInstallation.objects.bulk_create(installations)
                    installations = []
                    print(f"Successfully imported {success_count} records...")
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only print first 5 errors in detail
                    print(f"\nError processing row {index}:")
                    print("Row data:", row.to_dict())
                    print("Error:", str(e))
                continue
        
        # Create any remaining records
        if installations:
            SolarInstallation.objects.bulk_create(installations)

        print(f"\nImport completed. Successfully imported {success_count} records. Errors: {error_count}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise e

if __name__ == '__main__':
    # First, clear existing data
    print("Clearing existing data...")
    SolarInstallation.objects.all().delete()
    
    print("Starting import...")
    import_solar_data()