from fastapi import APIRouter, HTTPException
from ..db.mongodb import MongoDB
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
        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Get recent campaigns
        campaigns = await campaigns_collection.find().sort("created_at", -1).limit(limit).to_list(length=None)
        
        # Format the response
        formatted_campaigns = []
        for campaign in campaigns:
            formatted_campaigns.append({
                "id": str(campaign["_id"]),
                "name": campaign.get("name", "Unnamed Campaign"),
                "status": campaign.get("status", "unknown"),
                "totalEmails": campaign.get("total_emails", 0),
                "successful": campaign.get("successful", 0),
                "failed": campaign.get("failed", 0),
                "createdAt": campaign.get("created_at"),
                "startTime": campaign.get("start_time"),
                "endTime": campaign.get("end_time"),
                "duration": campaign.get("duration"),
                "successRate": round((campaign.get("successful", 0) / campaign.get("total_emails", 1)) * 100, 1) if campaign.get("total_emails", 0) > 0 else 0
            })
        
        return formatted_campaigns
        
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching campaigns: {str(e)}")

@router.get("/activity")
async def get_recent_activity(limit: int = 10):
    """Get recent activity for dashboard."""
    try:
        # This could include various activities like:
        # - Campaign creation
        # - Email sends
        # - User registrations
        # - Template updates
        # For now, we'll return campaign activities
        
        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Get recent campaigns as activity
        campaigns = await campaigns_collection.find().sort("created_at", -1).limit(limit).to_list(length=None)
        
        activities = []
        for campaign in campaigns:
            activities.append({
                "id": str(campaign["_id"]),
                "type": "campaign_created",
                "title": f"Campaign '{campaign.get('name', 'Unnamed')}' created",
                "description": f"Email campaign with {campaign.get('total_emails', 0)} recipients",
                "timestamp": campaign.get("created_at"),
                "status": campaign.get("status", "unknown"),
                "metadata": {
                    "campaign_id": str(campaign["_id"]),
                    "total_emails": campaign.get("total_emails", 0),
                    "successful": campaign.get("successful", 0),
                    "failed": campaign.get("failed", 0)
                }
            })
        
        return activities
        
    except Exception as e:
        logger.error(f"Error fetching activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching activity: {str(e)}") 