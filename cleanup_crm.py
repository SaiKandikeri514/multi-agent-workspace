from database.db_setup import SessionLocal, InternalCRM

def cleanup():
    session = SessionLocal()
    try:
        records = session.query(InternalCRM).all()
        
        sla_map = {
            "Standard": "Standard: 99.5%",
            "Premium": "Premium: 99.9%",
            "Ultra premium": "Ultra Premium: 99.99%"
        }
        
        for rec in records:
            level = rec.sla_level
            # Remove redundant ' SLA' (case insensitive)
            new_level = level.replace(" SLA", "").replace(" sla", "")
            
            # If it's just the keyword, add the percentage
            for key, val in sla_map.items():
                if new_level.strip().lower() == key.lower():
                    new_level = val
                    break
            
            rec.sla_level = new_level
            
        session.commit()
        print("CRM Cleanup successful.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    cleanup()
