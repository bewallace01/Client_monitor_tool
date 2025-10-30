from app.database.connection import SessionLocal
from app.models.event import Event
from datetime import datetime, timedelta

db = SessionLocal()

cutoff = datetime.now() - timedelta(hours=3)
events = db.query(Event).filter(Event.event_date > cutoff).order_by(Event.event_date.desc()).all()

tesla = [e for e in events if e.client and 'tesla' in e.client.name.lower()]
wells = [e for e in events if e.client and 'wells' in e.client.name.lower()]
microsoft = [e for e in events if e.client and 'microsoft' in e.client.name.lower()]
informa = [e for e in events if e.client and 'informa' in e.client.name.lower()]

print(f'Tesla events: {len(tesla)}')
print(f'Wells Fargo events: {len(wells)}')
print(f'Microsoft events: {len(microsoft)}')
print(f'Informa events: {len(informa)}')

if tesla:
    print(f'\nSample Tesla event:')
    print(f'  Title: {tesla[0].title}')
    print(f'  Source URL: {tesla[0].source_url[:80] if tesla[0].source_url else "None"}')
    print(f'  Source Type: {tesla[0].source_type}')

db.close()
