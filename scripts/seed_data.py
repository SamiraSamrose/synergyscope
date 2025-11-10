# File: scripts/seed_data.py
# Purpose: Load sample/seed data for demonstration

#!/usr/bin/env python3
"""
Seed Data Script
Populates the system with sample data for demonstration
"""

import asyncio
import json
from datetime import datetime, timedelta

async def seed_database():
    """Seed database with sample data"""
    print("Seeding sample data...")
    
    # Sample summoner data
    sample_summoners = [
        {"id": "summoner1", "name": "DemoPlayer1", "wins": 150, "losses": 120},
        {"id": "summoner2", "name": "DemoPlayer2", "wins": 180, "losses": 140},
        {"id": "summoner3", "name": "DemoPlayer3", "wins": 160, "losses": 135},
        {"id": "summoner4", "name": "DemoPlayer4", "wins": 145, "losses": 125},
        {"id": "summoner5", "name": "DemoPlayer5", "wins": 170, "losses": 150}
    ]
    
    # Sample match data
    sample_matches = []
    patches = ["14.17", "14.18", "14.19", "14.20", "14.21"]
    
    for i in range(100):
        match = {
            "match_id": f"match_{i}",
            "patch": patches[i % len(patches)],
            "timestamp": (datetime.now() - timedelta(days=100-i)).isoformat(),
            "participants": sample_summoners[:5]
        }
        sample_matches.append(match)
    
    # Save to files
    with open("data/sample_summoners.json", "w") as f:
        json.dump(sample_summoners, f, indent=2)
    
    with open("data/sample_matches.json", "w") as f:
        json.dump(sample_matches, f, indent=2)
    
    print(f"✓ Created {len(sample_summoners)} sample summoners")
    print(f"✓ Created {len(sample_matches)} sample matches")
    print("Seed data creation complete!")

if __name__ == "__main__":
    asyncio.run(seed_database())