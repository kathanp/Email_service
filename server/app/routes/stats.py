from fastapi import APIRouter, HTTPException
from ..db.mongodb import MongoDB
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def _is_development_mode():
    """Check if we're in development mode without database."""
    try:
        MongoDB.get_collection("stats")
        return False
    except:
        return True

@router.get("/summary")
async def get_stats_summary():
    """Get email campaign statistics summary for dashboard."""
    try:
        if _is_development_mode():
            # Development mode - return mock stats
            logger.info("Development mode: Mock stats summary")
            now = datetime.utcnow()
            return {
                "totalSent": 1250,
                "totalCustomers": 45,
                "sentToday": 25,
                "failedToday": 2,
                "totalToday": 27,
                "scheduledEmails": 0,
                "thisWeekSent": 180,
                "thisMonthSent": 750,
                "totalCampaigns": 12,
                "todayChange": 5,
                "weekChange": 15,
                "monthChange": 50,
                "todaySuccessRate": 92.6,
                "yesterdaySuccessRate": 88.9,
                "overallSuccessRate": 94.2,
                "lastUpdated": now,
                "periods": {
                    "today": {
                        "sent": 25,
                        "failed": 2,
                        "total": 27,
                        "success_rate": 92.6
                    },
                    "yesterday": {
                        "sent": 20,
                        "failed": 2,
                        "total": 22,
                        "success_rate": 88.9
                    },
                    "this_week": {
                        "sent": 180,
                        "failed": 12,
                        "total": 192
                    },
                    "this_month": {
                        "sent": 750,
                        "failed": 45,
                        "total": 795
                    }
                }
            }

        # Get the stats collection
        stats_collection = MongoDB.get_collection("stats")
        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Get overall stats with default values
        stats = await stats_collection.find_one({"_id": "email_stats"}) or {}
        
        # Calculate time periods
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Get campaigns for different time periods
        today_campaigns = await campaigns_collection.find({
            "created_at": {"$gte": today}
        }).to_list(length=None)
        
        yesterday_campaigns = await campaigns_collection.find({
            "created_at": {"$gte": yesterday, "$lt": today}
        }).to_list(length=None)
        
        this_week_campaigns = await campaigns_collection.find({
            "created_at": {"$gte": week_ago}
        }).to_list(length=None)
        
        this_month_campaigns = await campaigns_collection.find({
            "created_at": {"$gte": month_ago}
        }).to_list(length=None)
        
        # Calculate statistics with safe defaults
        total_sent = stats.get("total_emails_sent", 0)
        total_campaigns = stats.get("total_campaigns", 0)
        
        # Today's stats
        today_sent = sum(campaign.get("successful", 0) for campaign in today_campaigns)
        today_failed = sum(campaign.get("failed", 0) for campaign in today_campaigns)
        today_total = today_sent + today_failed
        
        # Yesterday's stats
        yesterday_sent = sum(campaign.get("successful", 0) for campaign in yesterday_campaigns)
        yesterday_failed = sum(campaign.get("failed", 0) for campaign in yesterday_campaigns)
        yesterday_total = yesterday_sent + yesterday_failed
        
        # This week's stats
        this_week_sent = sum(campaign.get("successful", 0) for campaign in this_week_campaigns)
        this_week_failed = sum(campaign.get("failed", 0) for campaign in this_week_campaigns)
        this_week_total = this_week_sent + this_week_failed
        
        # This month's stats
        this_month_sent = sum(campaign.get("successful", 0) for campaign in this_month_campaigns)
        this_month_failed = sum(campaign.get("failed", 0) for campaign in this_month_campaigns)
        this_month_total = this_month_sent + this_month_failed
        
        # Calculate changes
        today_change = today_total - yesterday_total
        week_change = this_week_total - (total_sent - this_week_total)  # Rough estimate
        month_change = this_month_total - (total_sent - this_month_total)  # Rough estimate
        
        # Get customer count (users collection)
        users_collection = MongoDB.get_collection("users")
        total_customers = await users_collection.count_documents({})
        
        # Calculate success rates
        today_success_rate = (today_sent / today_total * 100) if today_total > 0 else 0
        yesterday_success_rate = (yesterday_sent / yesterday_total * 100) if yesterday_total > 0 else 0
        overall_success_rate = (total_sent / (total_sent + stats.get("total_emails_failed", 0)) * 100) if (total_sent + stats.get("total_emails_failed", 0)) > 0 else 0
        
        return {
            "totalSent": total_sent,
            "totalCustomers": total_customers,
            "sentToday": today_sent,
            "failedToday": today_failed,
            "totalToday": today_total,
            "scheduledEmails": 0,  # You can implement this if you have scheduled emails
            "thisWeekSent": this_week_sent,
            "thisMonthSent": this_month_sent,
            "totalCampaigns": total_campaigns,
            "todayChange": today_change,
            "weekChange": week_change,
            "monthChange": month_change,
            "todaySuccessRate": round(today_success_rate, 1),
            "yesterdaySuccessRate": round(yesterday_success_rate, 1),
            "overallSuccessRate": round(overall_success_rate, 1),
            "lastUpdated": stats.get("last_updated", now),
            "periods": {
                "today": {
                    "sent": today_sent,
                    "failed": today_failed,
                    "total": today_total,
                    "success_rate": round(today_success_rate, 1)
                },
                "yesterday": {
                    "sent": yesterday_sent,
                    "failed": yesterday_failed,
                    "total": yesterday_total,
                    "success_rate": round(yesterday_success_rate, 1)
                },
                "this_week": {
                    "sent": this_week_sent,
                    "failed": this_week_failed,
                    "total": this_week_total
                },
                "this_month": {
                    "sent": this_month_sent,
                    "failed": this_month_failed,
                    "total": this_month_total
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@router.get("/campaigns")
async def get_recent_campaigns(limit: int = 10):
    """Get recent email campaigns."""
    try:
        if _is_development_mode():
            # Development mode - return mock campaigns
            logger.info("Development mode: Mock campaigns")
            now = datetime.utcnow()
            return [
                {
                    "id": "campaign_1",
                    "name": "Welcome Campaign",
                    "status": "completed",
                    "total_emails": 150,
                    "successful": 145,
                    "failed": 5,
                    "duration": 120,
                    "created_at": (now - timedelta(hours=2)).isoformat(),
                    "template_name": "Welcome Template",
                    "file_name": "contacts.xlsx"
                },
                {
                    "id": "campaign_2",
                    "name": "Newsletter Campaign",
                    "status": "completed",
                    "total_emails": 200,
                    "successful": 190,
                    "failed": 10,
                    "duration": 180,
                    "created_at": (now - timedelta(days=1)).isoformat(),
                    "template_name": "Newsletter Template",
                    "file_name": "subscribers.xlsx"
                }
            ]

        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Get recent campaigns sorted by creation date
        campaigns = await campaigns_collection.find().sort("created_at", -1).limit(limit).to_list(length=None)
        
        # Convert ObjectId to string and format data for frontend
        formatted_campaigns = []
        for campaign in campaigns:
            formatted_campaign = {
                "id": str(campaign["_id"]),
                "name": campaign.get("name", "Unnamed Campaign"),
                "status": campaign.get("status", "unknown"),
                "total_emails": campaign.get("total_emails", 0),
                "successful": campaign.get("successful", 0),
                "failed": campaign.get("failed", 0),
                "duration": campaign.get("duration", 0),
                "created_at": campaign.get("created_at", datetime.utcnow()).isoformat(),
                "template_name": campaign.get("template_name", "Unknown Template"),
                "file_name": campaign.get("file_name", "Unknown File")
            }
            formatted_campaigns.append(formatted_campaign)
        
        return formatted_campaigns
        
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching campaigns: {str(e)}")

@router.get("/activity")
async def get_recent_activity(limit: int = 10):
    """Get recent activity for dashboard."""
    try:
        if _is_development_mode():
            # Development mode - return mock activity
            logger.info("Development mode: Mock activity")
            now = datetime.utcnow()
            return [
                {
                    "id": "activity_1",
                    "type": "email_campaign",
                    "message": "Email campaign sent to 150 contacts",
                    "time": (now - timedelta(hours=2)).isoformat(),
                    "status": "success",
                    "details": {
                        "emails_sent": 145,
                        "emails_failed": 5,
                        "success_rate": 96.7
                    }
                },
                {
                    "id": "activity_2",
                    "type": "email_campaign",
                    "message": "Email campaign sent to 200 contacts",
                    "time": (now - timedelta(days=1)).isoformat(),
                    "status": "success",
                    "details": {
                        "emails_sent": 190,
                        "emails_failed": 10,
                        "success_rate": 95.0
                    }
                }
            ]

        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Get recent campaigns and convert to activity format
        campaigns = await campaigns_collection.find().sort("created_at", -1).limit(limit).to_list(length=None)
        
        activities = []
        for campaign in campaigns:
            activities.append({
                "id": str(campaign["_id"]),
                "type": "email_campaign",
                "message": f"Email campaign sent to {campaign.get('total_contacts', 0)} contacts",
                "time": campaign["created_at"].isoformat(),
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