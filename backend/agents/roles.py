from dataclasses import dataclass


@dataclass
class ExpertRole:
    name: str
    description: str


CHEF = ExpertRole(
    name="ChefExpert",
    description="Master chef focusing on flavor, timing, and technique."
)
NUTRITION = ExpertRole(
    name="NutritionExpert",
    description="Provides macronutrient balance and dietary restrictions guidance."
)
TOOL_PROCESS = ExpertRole(
    name="ToolProcessEngineer",
    description="Optimizes tool usage and workflow efficiency."
)
NEWBIE = ExpertRole(
    name="NewbieCoach",
    description="Translates steps for beginners with clear guidance."
)
SAFETY = ExpertRole(
    name="SafetyOfficer",
    description="Monitors safety hazards and handling instructions."
)
CHAIR = ExpertRole(
    name="CommitteeChair",
    description="Summarizes and drives consensus across experts."
)

ALL_EXPERTS = [CHEF, NUTRITION, TOOL_PROCESS, NEWBIE, SAFETY]
