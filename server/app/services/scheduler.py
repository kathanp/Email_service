from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.email_service import EmailService

class EmailScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.email_service = EmailService()
        self.scheduler.start()

    async def schedule_daily_email(self, customer_id: str, time: str, template_id: str):
        """Schedule a daily email for a specific customer"""
        hour, minute = time.split(':')
        self.scheduler.add_job(
            self.email_service.send_email,
            CronTrigger(hour=hour, minute=minute),
            args=[customer_id, template_id],
            id=f"email_{customer_id}_{template_id}"
        )

    def remove_schedule(self, customer_id: str, template_id: str):
        """Remove a scheduled email"""
        self.scheduler.remove_job(f"email_{customer_id}_{template_id}")
