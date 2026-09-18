from enum import Enum
from pydantic import BaseModel, Field, model_validator, ValidationError
from datetime import datetime


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: list[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def mission_Validation_rules(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')

        crew_ranks = False
        for member in self.crew:
            if member.rank in (Rank.COMMANDER, Rank.CAPTAIN):
                crew_ranks = True
        if not crew_ranks:
            raise ValueError("Must have at least one Commander or Captain")

        if self.duration_days > 365:
            experienced_count = 0
            for member in self.crew:
                if member.years_experience >= 5:
                    experienced_count += 1
            experienced_crew = experienced_count / len(self.crew)
            if experienced_crew < 0.5:
                raise ValueError("Long missions (> 365 days)"
                                 " need 50% experienced crew (5+ years)")

        for member in self.crew:
            if not member.is_active:
                raise ValueError("All crew members must be active")

        return self


def test_valid_mission() -> None:
    print("Space Mission Crew Validation")
    print("=========================================")

    crew = [
        CrewMember(
            member_id="C001",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=42,
            specialization="Mission Command",
            years_experience=15
        ),
        CrewMember(
            member_id="C002",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=35,
            specialization="Navigation",
            years_experience=8
        ),
        CrewMember(
            member_id="C003",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=29,
            specialization="Engineering",
            years_experience=5
        )
    ]

    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2026, 9, 15, 17, 52, 0),
        duration_days=900,
        crew=crew,
        budget_millions=2500.0,
    )

    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(f"- {member.name} ({member.rank}) - {member.specialization}")
    print()


def test_invalid_mission() -> None:
    print("=========================================")
    print("Expected validation error:")

    crew = [
            CrewMember(
                member_id="C004",
                name="Bob Wilson",
                rank=Rank.OFFICER,
                age=30,
                specialization="Engineering",
                years_experience=3
            )
    ]

    try:
        SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Lunar Colony Establishment",
            destination="Moon",
            launch_date=datetime(2026, 9, 15, 17, 52, 0),
            duration_days=100,
            crew=crew,
            budget_millions=500.0,
        )
    except ValidationError as err:
        print(err.errors()[0]["msg"])


if __name__ == "__main__":
    test_valid_mission()
    test_invalid_mission()
