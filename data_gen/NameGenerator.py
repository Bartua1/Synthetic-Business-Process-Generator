
import random

class NameGenerator:
    def __init__(self):
        self.FIRST_WORDS = [
            "Submit",
            "Review",
            "Approve",
            "Verify",
            "Check",
            "Update",
            "Process",
            "Validate",
            "Evaluate",
            "Confirm",
            "Send",
            "Receive",
            "Forward",
            "Archive",
            "Generate",
            "Schedule",
            "Track",
            "Monitor",
            "Record",
            "Assign",
            "Initiate",
            "Complete",
            "Modify",
            "Register",
            "Create",
            "Assess",
            "Calculate",
            "Document",
            "File",
            "Handle",
            "Prepare",
            "Analyze",
            "Store",
            "Transfer",
            "Notify",
            "Log",
            "Enter",
            "Export",
            "Import",
            "Plan",
            "Route",
            "Sign",
            "Scan",
            "Print",
            "Match",
            "Collect",
            "Release",
            "Save",
            "Format",
            "Dispatch"
        ]

        # Second words (objects/subjects)
        self.SECOND_WORDS = [
            "Request",
            "Form",
            "Application",
            "Documents",
            "Dates",
            "Schedule",
            "Calendar",
            "Period",
            "Status",
            "Approval",
            "Records",
            "Details",
            "Information",
            "Notification",
            "Coverage",
            "Balance",
            "Duration",
            "Eligibility",
            "Submission",
            "Workflow",
            "Data",
            "History",
            "Authorization",
            "Confirmation",
            "Availability",
            "Policy",
            "Requirements",
            "Verification",
            "Certificate",
            "Permission",
            "Documentation",
            "Timeframe",
            "Evidence",
            "Proof",
            "Response",
            "Report",
            "Comments",
            "Feedback",
            "Reference",
            "Timeline",
            "Signature",
            "Attachments",
            "Compliance",
            "Guidelines",
            "Credentials",
            "Conditions",
            "Agreement",
            "Summary",
            "Statistics",
            "Validation"
        ]

    def get_all_names(self):
        """Return all possible names."""
        return [f'{first} {second}' for first in self.FIRST_WORDS for second in self.SECOND_WORDS]

    def get_total(self):
        """Return the total number of possible names."""
        return len(self.FIRST_WORDS) * len(self.SECOND_WORDS)