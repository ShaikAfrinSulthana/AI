import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class FeedbackHandler:
    def __init__(self):
        self.feedback_storage = []
        logger.info("FeedbackHandler initialized")
    
    def submit_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit and store user feedback"""
        try:
            feedback_id = str(len(self.feedback_storage) + 1)
            
            feedback_record = {
                "feedback_id": feedback_id,
                "session_id": feedback_data["session_id"],
                "message_id": feedback_data["message_id"],
                "rating": feedback_data["rating"],
                "category": feedback_data["category"],
                "comment": feedback_data.get("comment", ""),
                "timestamp": datetime.now().isoformat(),
                "metadata": feedback_data.get("metadata", {})
            }
            
            self.feedback_storage.append(feedback_record)
            
            logger.info(f"Feedback received - Rating: {feedback_data['rating']}, Category: {feedback_data['category']}")
            
            return {
                "feedback_id": feedback_id,
                "status": "success",
                "message": "Thank you for your feedback!",
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return {
                "feedback_id": None,
                "status": "error",
                "message": "Failed to submit feedback",
                "timestamp": datetime.now()
            }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get feedback analytics and statistics"""
        try:
            if not self.feedback_storage:
                return {
                    "total_feedback": 0,
                    "average_rating": 0,
                    "rating_distribution": {},
                    "category_distribution": {}
                }
            
            total = len(self.feedback_storage)
            ratings = [f["rating"] for f in self.feedback_storage if f["rating"] is not None]
            average_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Rating distribution
            rating_dist = {}
            for i in range(1, 6):
                rating_dist[str(i)] = len([f for f in self.feedback_storage if f["rating"] == i])
            
            # Category distribution
            category_dist = {}
            for feedback in self.feedback_storage:
                category = feedback.get("category", "general")
                category_dist[category] = category_dist.get(category, 0) + 1
            
            return {
                "total_feedback": total,
                "average_rating": round(average_rating, 2),
                "rating_distribution": rating_dist,
                "category_distribution": category_dist,
                "recent_feedback": self.feedback_storage[-10:]
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback analytics: {e}")
            return {}