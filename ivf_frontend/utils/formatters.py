from datetime import datetime, timedelta
from typing import Optional


class DataFormatter:
    """Data formatting utilities for timestamps, confidence, etc."""

    # ---------------------------------------------------------
    # TIMESTAMP FORMATTING
    # ---------------------------------------------------------
    @staticmethod
    def format_timestamp(timestamp, format_type: str = "relative") -> str:
        """Format timestamp for display inside message bubbles."""

        try:
            # Convert ISO string → datetime
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                dt = timestamp

            if format_type == "relative":
                return DataFormatter._relative_time(dt)
            elif format_type == "short":
                return dt.strftime("%H:%M")
            else:
                return dt.strftime("%Y-%m-%d %H:%M:%S")

        except Exception:
            return "Unknown time"

    @staticmethod
    def _relative_time(dt: datetime) -> str:
        """Human-friendly relative time."""
        now = datetime.now()
        diff = now - dt

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() // 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() // 3600)
            return f"{hours}h ago"
        else:
            return dt.strftime("%b %d")  # Example: Jan 25

    # ---------------------------------------------------------
    # CONFIDENCE BADGE (Pink Theme Compatible)
    # ---------------------------------------------------------
    @staticmethod
    def format_confidence_badge(score: Optional[float]) -> str:
        """
        Returns a small pink-themed confidence badge HTML.
        Designed to be rendered inside assistant message bubble.
        """

        if score is None:
            return ""

        pct = f"{score*100:.0f}%"

        # color logic (matches soft IVF theme)
        if score >= 0.8:
            color = "var(--accent-primary)"
        elif score >= 0.6:
            color = "#ffb3d1"
        elif score >= 0.4:
            color = "#ff9ec2"
        else:
            color = "#ff7aa8"

        return f"""
        <span style="
            display:inline-block;
            background: {color};
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.70rem;
            margin-left: 6px;
        ">
            Confidence: {pct}
        </span>
        """

    # ---------------------------------------------------------
    # SIMPLE EMOJI CONFIDENCE (Backward Compatible)
    # ---------------------------------------------------------
    @staticmethod
    def format_confidence_score(score: float) -> str:
        """Old emoji version — kept for compatibility."""
        if score >= 0.8:
            return f"🟢 {score:.1%}"
        elif score >= 0.6:
            return f"🟡 {score:.1%}"
        elif score >= 0.4:
            return f"🟠 {score:.1%}"
        else:
            return f"🔴 {score:.1%}"
