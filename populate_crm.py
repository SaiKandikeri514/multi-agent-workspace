from database.db_setup import SessionLocal, InternalCRM
import sys

def populate():
    session = SessionLocal()
    try:
        new_customers = [
            {"company_name": "Global Synergy Inc", "sla_level": "Standard SLA: 99.5%", "status": "Active"},
            {"company_name": "Titanium Logistics", "sla_level": "Premium SLA: 99.9%", "status": "Maintenance"},
            {"company_name": "Aether Cloud Services", "sla_level": "Ultra premium SLA: 99.99%", "status": "Active"},
            {"company_name": "Vortex Research", "sla_level": "Ultra premium SLA: 99.99%", "status": "Warning"}
        ]
        
        for cust in new_customers:
            # Check if exists to avoid duplicates
            existing = session.query(InternalCRM).filter(InternalCRM.company_name == cust["company_name"]).first()
            if not existing:
                new_rec = InternalCRM(**cust)
                session.add(new_rec)
        
        session.commit()
        print("Successfully added 4 new customers to CRM.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate()
