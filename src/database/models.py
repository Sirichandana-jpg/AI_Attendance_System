from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Student:
    id: int
    student_id: str
    name: str
    department: str
    created_at: str

@dataclass
class FaceEmbedding:
    id: int
    student_id: str
    embedding: List[float]
    model_name: str
    created_at: str

@dataclass
class AttendanceRecord:
    id: int
    student_id: str
    date: str
    time: str
    source: str
    confidence: float
    status: str
    created_at: str

@dataclass
class AttendanceReportItem:
    id: int
    student_id: str
    name: str
    department: str
    date: str
    time: str
    source: str
    confidence: float
    status: str
