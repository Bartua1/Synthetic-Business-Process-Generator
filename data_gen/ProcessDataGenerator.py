import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional
from tqdm import tqdm

class ProcessDataGenerator:
    def __init__(self, process_graph: Dict[str, List[str]],
                 num_cases: int = 100,
                 start_date: datetime = datetime(2023, 1, 1),
                 end_date: datetime = datetime(2023, 12, 31),
                 lmstudio_connector = None,
                 process_name: str = "Generic Process"):
        """
        Initialize the Process Data Generator.

        Args:
            process_graph: Dictionary representing the process flow
            num_cases: Number of cases to generate
            start_date: Start date for the event log
            end_date: End date for the event log
            lmstudio_connector: Connector for LMStudio
            process_name: Name of the process (used for generating relevant departments)
        """
        self.process_graph = process_graph
        self.num_cases = num_cases
        self.start_date = start_date
        self.end_date = end_date
        self.process_name = process_name
        self.connector = lmstudio_connector

        # Generate departments based on process name
        self.departments = self._generate_departments()

        # Configuration for realistic data generation
        self.resources = self._generate_resources()
        self.cost_ranges = self._generate_cost_ranges()

    def _generate_departments(self) -> List[str]:
        """Generate relevant departments based on process name using LMStudio."""
        if self.connector:
            prompt = f"""Given the process name '{self.process_name}', list 4-6 relevant department names that would be involved in this process.
            Return only the department names separated by commas, no additional text.
            Example format: Sales, Operations, Customer Service, Legal"""

            try:
                departments_str = self.connector.get_answer(prompt)
                departments = [dept.strip() for dept in departments_str.split(',')]
                return departments
            except Exception as e:
                print(f"Error generating departments: {e}")
                # Fallback departments
                return ["Sales", "Operations", "Customer Service", "Finance", "Legal"]
        else:
            # Fallback departments if no connector is available
            return ["Sales", "Operations", "Customer Service", "Finance", "Legal"]

    def _generate_resources(self) -> List[str]:
        """Generate resource names based on departments."""
        resources = []
        for dept in self.departments:
            # Generate 2-3 resources per department
            num_resources = random.randint(2, 3)
            dept_prefix = dept.split()[0]  # Take first word of department name
            resources.extend([f"{dept_prefix}_Agent_{i}" for i in range(1, num_resources + 1)])
        return resources

    def _generate_cost_ranges(self) -> Dict[str, tuple]:
        """Generate cost ranges for each department."""
        # if self.connector:
        #     prompt = f"""Given these departments for the process '{self.process_name}': {', '.join(self.departments)},
        #     suggest an hourly cost range (min,max) for each department.
        #     Return only the numbers separated by commas for each department, one department per line.
        #     Example format:
        #     50,150
        #     60,180
        #     45,120"""

        #     try:
        #         ranges_str = self.connector.get_answer(prompt)
        #         ranges = {}
        #         for dept, range_str in zip(self.departments, ranges_str.split('\n')):
        #             min_cost, max_cost = map(float, range_str.strip().split(','))
        #             ranges[dept] = (min_cost, max_cost)
        #         return ranges
        #     except Exception as e:
        #         print(f"Error generating cost ranges: {e}")
        #         return self._generate_default_cost_ranges()
        # else:
        #     return self._generate_default_cost_ranges()
        return self._generate_default_cost_ranges()

    def _generate_default_cost_ranges(self) -> Dict[str, tuple]:
        """Generate default cost ranges if LMStudio is not available."""
        return {
            dept: (50 + i * 20, 150 + i * 20)
            for i, dept in enumerate(self.departments)
        }

    def _generate_case_attributes(self) -> Dict:
        """Generate attributes for a single case."""
        if self.connector:
            prompt = f"""Given the process '{self.process_name}', suggest a product category name.
            Return only the category name, no additional text."""
            try:
                product_category = self.connector.get_answer(prompt).strip()
            except:
                product_category = random.choice(["Type A", "Type B", "Type C"])
        else:
            product_category = random.choice(["Type A", "Type B", "Type C"])

        return {
            "customer_id": f"CUST_{random.randint(1000, 9999)}",
            "priority": random.choice(["Low", "Medium", "High"]),
            "channel": random.choice(["Web", "Phone", "Email", "In-Person"]),
            "department": random.choice(self.departments),
            "product_category": product_category,
            "value": round(random.uniform(100, 10000), 2)
        }

    # ... [Rest of the methods remain the same as in the previous version] ...

    def _generate_activity_attributes(self, activity: str, department: str) -> Dict:
        """Generate attributes for a single activity."""
        base_duration = random.randint(30, 480)  # 30 mins to 8 hours in minutes
        cost_range = self.cost_ranges[department]

        # Filter resources by department
        dept_prefix = department.split()[0]
        dept_resources = [r for r in self.resources if r.startswith(dept_prefix)]

        return {
            "resource": random.choice(dept_resources if dept_resources else self.resources),
            "duration_minutes": base_duration,
            "cost": round(random.uniform(*cost_range), 2),
            "status": random.choice(["Completed", "Delayed", "Expedited"]),
            "system": random.choice(["System A", "System B", "System C"]),
            "automated": random.choice([True, False])
        }

    def _generate_timestamp(self, base_time: datetime, activity_duration: int) -> datetime:
        """Generate a realistic timestamp considering working hours."""
        working_hours = range(9, 18)  # 9 AM to 6 PM

        current_time = base_time + timedelta(minutes=activity_duration)

        # If outside working hours, move to next working day
        while current_time.hour not in working_hours or current_time.weekday() >= 5:
            if current_time.hour >= 18:
                current_time = current_time.replace(hour=9, minute=0)
                current_time += timedelta(days=1)
            elif current_time.hour < 9:
                current_time = current_time.replace(hour=9, minute=0)

            if current_time.weekday() >= 5:  # Weekend
                current_time += timedelta(days=8 - current_time.weekday())

        return current_time

    def _generate_case_path(self) -> List[str]:
        """Generate a valid path through the process graph."""
        path = ['START']
        current = 'START'

        while current != 'END':
            possible_next = self.process_graph[current]
            current = random.choice(possible_next)
            path.append(current)

        return path

    def generate_data(self) -> pd.DataFrame:
        """Generate complete event log data with progress bar."""
        events = []

        # Create progress bar for case generation
        with tqdm(total=self.num_cases, desc="Generating cases") as pbar:
            for case_id in range(1, self.num_cases + 1):
                case_attrs = self._generate_case_attributes()
                path = self._generate_case_path()

                # Initialize case start time randomly between start_date and end_date
                current_time = self.start_date + (self.end_date - self.start_date) * random.random()

                for activity in path:
                    if activity in ['START', 'END']:
                        continue

                    activity_attrs = self._generate_activity_attributes(activity, case_attrs['department'])

                    # Generate timestamp and calculate complete_timestamp
                    timestamp = self._generate_timestamp(current_time, 0)
                    complete_timestamp = self._generate_timestamp(timestamp, activity_attrs['duration_minutes'])
                    current_time = complete_timestamp

                    event = {
                        'case_id': f"CASE_{case_id:05d}",
                        'activity': activity,
                        'timestamp': timestamp,
                        'complete_timestamp': complete_timestamp,
                        **case_attrs,
                        **activity_attrs
                    }
                    events.append(event)

                pbar.update(1)

        # Create DataFrame and sort by timestamp
        df = pd.DataFrame(events)
        df = df.sort_values(['case_id', 'timestamp'])

        return df

    def save_to_csv(self, filename: str = 'process_data.csv'):
        """Generate data and save to CSV file."""
        df = self.generate_data()
        df.to_csv("data/" + filename, index=False)
        print(f"Generated {len(df)} events for {self.num_cases} cases")
        print(f"Data saved to {filename}")

    def get_data_summary(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """Get summary statistics of the generated data."""
        if df is None:
            df = self.generate_data()

        summary = {
            'total_cases': df['case_id'].nunique(),
            'total_events': len(df),
            'unique_activities': df['activity'].nunique(),
            'unique_resources': df['resource'].nunique(),
            'avg_case_duration': (df.groupby('case_id')['complete_timestamp'].max() -
                                df.groupby('case_id')['timestamp'].min()).mean(),
            'avg_events_per_case': len(df) / df['case_id'].nunique(),
            'total_cost': df['cost'].sum(),
            'avg_cost_per_case': df.groupby('case_id')['cost'].sum().mean()
        }

        return summary