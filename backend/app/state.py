"""Shared pipeline state. See docs/architecture.md for the design this mirrors."""

from typing import Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    raw_courses: list[str] = Field(default_factory=list)
    raw_projects: list[str] = Field(default_factory=list)
    github_urls: list[str] = Field(default_factory=list)
    target_role: Optional[str] = None
    target_job_description: Optional[str] = None


class SkillEntry(BaseModel):
    name: str
    evidence: str
    confidence: Literal["low", "medium", "high"]


class RequirementSkill(BaseModel):
    name: str
    frequency: float  # fraction of postings mentioning this skill, 0-1


class IndustryRequirements(BaseModel):
    role: str
    skills: list[RequirementSkill] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    tools: list[RequirementSkill] = Field(default_factory=list)


class SkillMapping(BaseModel):
    academic_concept: str
    industry_skill: str
    source: Literal["taxonomy", "inferred"]


class GapEntry(BaseModel):
    skill: str
    current_level: float  # 0-1, how strongly the student already demonstrates this
    market_importance: Literal["low", "medium", "high"]
    priority: Literal["low", "medium", "high", "critical"]
    frequency: float  # fraction of this role's job postings mentioning the skill, 0-1


class MissionRequirement(BaseModel):
    description: str
    addresses_gap: str  # must match a GapEntry.skill


class Mission(BaseModel):
    title: str
    brief: str
    requirements: list[MissionRequirement] = Field(default_factory=list)


class SprintSpec(BaseModel):
    index: int
    title: str
    objective: str
    requirements: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    addresses_gap: str


class CoverageReport(BaseModel):
    covered_gaps: list[str] = Field(default_factory=list)
    uncovered_gaps: list[str] = Field(default_factory=list)
    recommendation: Optional[str] = None


class PipelineState(TypedDict, total=False):
    student_profile: StudentProfile
    skill_graph: list[SkillEntry]
    github_fetch_issues: list[str]  # repo URLs that failed to fetch, so thin evidence is explained
    industry_requirements: IndustryRequirements
    skill_map: list[SkillMapping]
    gaps: list[GapEntry]
    mission: Optional[Mission]
    coverage: Optional[CoverageReport]
    revision_count: int
    final_plan: Optional[dict]
