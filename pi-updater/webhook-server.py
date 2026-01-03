from fastapi import FastAPI, Header, HTTPException
import subprocess
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='/home/pi/breatheasy/webhook.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Breatheasy Webhook Updater")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@app.post("/update")
async def trigger_update(authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {WEBHOOK_SECRET}":
        logging.warning("Unauthorized webhook attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        logging.info("Starting service update...")

        # Pull latest images
        logging.info("Pulling latest Docker images...")
        result_pull = subprocess.run(["docker", "compose", "pull"],
                                   capture_output=True, text=True, check=True)
        logging.info(f"Pull result: {result_pull.stdout}")

        # Restart services
        logging.info("Restarting services...")
        result_up = subprocess.run(["docker", "compose", "up", "-d"],
                                 capture_output=True, text=True, check=True)
        logging.info(f"Up result: {result_up.stdout}")

        # Clean up old images
        logging.info("Cleaning up old images...")
        result_prune = subprocess.run(["docker", "image", "prune", "-f"],
                                    capture_output=True, text=True, check=True)
        logging.info(f"Prune result: {result_prune.stdout}")

        logging.info("Service update completed successfully")
        return {
            "status": "success",
            "message": "Services updated successfully",
            "timestamp": datetime.utcnow().isoformat()
        }

    except subprocess.CalledProcessError as e:
        error_msg = f"Update failed: {e.stderr}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during update: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/logs")
async def get_logs(lines: int = 50):
    """Get recent webhook logs"""
    try:
        with open('/home/pi/breatheasy/webhook.log', 'r') as f:
            lines_content = f.readlines()[-lines:]
        return {"logs": lines_content}
    except FileNotFoundError:
        return {"logs": ["No logs available yet"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
