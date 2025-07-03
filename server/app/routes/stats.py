from fastapi import APIRouter, HTTPException
from app.db.mongodb import MongoDB
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/summary")
async def get_stats_summary():
    """Get email campaign statistics summary for dashboard."""
    try:
        # Get the stats collection
        stats_collection = MongoDB.get_collection("stats")
        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Get overall stats
        stats = await stats_collection.find_one({"_id": "email_stats"})
        
        # Calculate this week's stats
        week_ago = datetime.utcnow() - timedelta(days=7)
        this_week_campaigns = await campaigns_collection.find({
            "date": {"$gte": week_ago}
        }).to_list(length=None)
        
        # Calculate today's stats
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_campaigns = await campaigns_collection.find({
            "date": {"$gte": today}
        }).to_list(length=None)
        
        # Calculate totals
        total_sent = stats.get("total_emails_sent", 0) if stats else 0
        total_campaigns = stats.get("total_campaigns", 0) if stats else 0
        
        # Calculate this week's sent emails
        this_week_sent = sum(campaign.get("emails_sent", 0) for campaign in this_week_campaigns)
        
        # Calculate today's sent emails
        today_sent = sum(campaign.get("emails_sent", 0) for campaign in today_campaigns)
        
        # Get customer count (you can implement this based on your customer collection)
        customers_collection = MongoDB.get_collection("users")
        total_customers = await customers_collection.count_documents({})
        
        return {
            "totalSent": total_sent,
            "totalCustomers": total_customers,
            "sentToday": today_sent,
            "scheduledEmails": 0,  # You can implement this if you have scheduled emails
            "thisWeekSent": this_week_sent,
            "totalCampaigns": total_campaigns,
            "lastUpdated": stats.get("last_updated", datetime.utcnow()) if stats else datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@router.get("/campaigns")
async def get_recent_campaigns(limit: int = 10):
    """Get recent email campaigns."""
    try:
        campaigns_collection = MongoDB.get_collection("campaigns")
        
        campaigns = await campaigns_collection.find().sort("date", -1).limit(limit).to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for campaign in campaigns:
            campaign["_id"] = str(campaign["_id"])
            campaign["date"] = campaign["date"].isoformat()
        
        return campaigns
        
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching campaigns: {str(e)}")

@router.get("/activity")
async def get_recent_activity(limit: int = 10):
    """Get recent activity for dashboard."""
    try:
        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Get recent campaigns and convert to activity format
        campaigns = await campaigns_collection.find().sort("date", -1).limit(limit).to_list(length=None)
        
        activities = []
        for campaign in campaigns:
            activities.append({
                "id": str(campaign["_id"]),
                "type": "email_campaign",
                "message": f"Email campaign sent to {campaign.get('total_contacts', 0)} contacts",
                "time": campaign["date"].isoformat(),
                "status": "success" if campaign.get("emails_sent", 0) > 0 else "error",
                "details": {
                    "emails_sent": campaign.get("emails_sent", 0),
                    "emails_failed": campaign.get("emails_failed", 0),
                    "success_rate": campaign.get("success_rate", 0)
                }
            })
        
        return activities
        
    except Exception as e:
        logger.error(f"Error fetching activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching activity: {str(e)}") 