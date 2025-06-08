from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, validator

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType, School, Region, City, District

router = APIRouter()


class SchoolBase(BaseModel):
    """Base schema for school data"""
    name: str
    address: str
    region_id: int
    city_id: int
    district_id: int
    
    model_config = ConfigDict(from_attributes=True)
    
    @validator('name', 'address')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v


class SchoolResponse(SchoolBase):
    """Response schema for school"""
    id: int
    region_name: Optional[str] = None
    city_name: Optional[str] = None
    district_name: Optional[str] = None
    created_at: str
    updated_at: str


@router.get("/", response_model=List[Dict[str, Any]])
async def get_schools(
    region_id: Optional[int] = None,
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schools with optional filtering by region, city, or district"""
    
    # Start with base query
    query = db.query(School)
    
    # Apply filters if provided
    if region_id:
        query = query.filter(School.region_id == region_id)
    if city_id:
        query = query.filter(School.city_id == city_id)
    if district_id:
        query = query.filter(School.district_id == district_id)
    
    # Execute query
    schools = query.all()
    
    # Format response
    result = []
    for school in schools:
        # Get related region, city, and district names
        region = db.query(Region).filter(Region.id == school.region_id).first()
        city = db.query(City).filter(City.id == school.city_id).first()
        district = db.query(District).filter(District.id == school.district_id).first()
        
        result.append({
            "id": school.id,
            "name": school.name,
            "address": school.address,
            "region_id": school.region_id,
            "region_name": region.name if region else None,
            "city_id": school.city_id,
            "city_name": city.name if city else None,
            "district_id": school.district_id,
            "district_name": district.name if district else None,
            "created_at": school.created_at.isoformat() if school.created_at else None,
            "updated_at": school.updated_at.isoformat() if school.updated_at else None
        })
    
    return result


@router.get("/{school_id}", response_model=Dict[str, Any])
async def get_school(
    school_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific school by ID"""
    
    # Get school
    school = db.query(School).filter(School.id == school_id).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Get related region, city, and district names
    region = db.query(Region).filter(Region.id == school.region_id).first()
    city = db.query(City).filter(City.id == school.city_id).first()
    district = db.query(District).filter(District.id == school.district_id).first()
    
    # Return school information
    return {
        "id": school.id,
        "name": school.name,
        "address": school.address,
        "region_id": school.region_id,
        "region_name": region.name if region else None,
        "city_id": school.city_id,
        "city_name": city.name if city else None,
        "district_id": school.district_id,
        "district_name": district.name if district else None,
        "created_at": school.created_at.isoformat() if school.created_at else None,
        "updated_at": school.updated_at.isoformat() if school.updated_at else None
    }


@router.get("/regions", response_model=List[Dict[str, Any]])
async def get_regions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all regions"""
    
    regions = db.query(Region).all()
    
    result = []
    for region in regions:
        result.append({
            "id": region.id,
            "name": region.name
        })
    
    return result


@router.get("/cities", response_model=List[Dict[str, Any]])
async def get_cities(
    region_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cities with optional filtering by region"""
    
    # Start with base query
    query = db.query(City)
    
    # Apply filter if provided
    if region_id:
        query = query.filter(City.region_id == region_id)
    
    # Execute query
    cities = query.all()
    
    result = []
    for city in cities:
        result.append({
            "id": city.id,
            "name": city.name,
            "region_id": city.region_id
        })
    
    return result


@router.get("/districts", response_model=List[Dict[str, Any]])
async def get_districts(
    city_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get districts with optional filtering by city"""
    
    # Start with base query
    query = db.query(District)
    
    # Apply filter if provided
    if city_id:
        query = query.filter(District.city_id == city_id)
    
    # Execute query
    districts = query.all()
    
    result = []
    for district in districts:
        result.append({
            "id": district.id,
            "name": district.name,
            "city_id": district.city_id
        })
    
    return result


@router.post("/", response_model=Dict[str, Any])
async def create_school(
    school_data: SchoolBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new school (admin only)"""
    
    # Check if user is an admin
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only admins can create schools."
        )
    
    # Validate that region, city, and district exist
    region = db.query(Region).filter(Region.id == school_data.region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found"
        )
    
    city = db.query(City).filter(City.id == school_data.city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    district = db.query(District).filter(District.id == school_data.district_id).first()
    if not district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="District not found"
        )
    
    # Create new school
    try:
        new_school = School(
            name=school_data.name,
            address=school_data.address,
            region_id=school_data.region_id,
            city_id=school_data.city_id,
            district_id=school_data.district_id
        )
        
        db.add(new_school)
        db.commit()
        db.refresh(new_school)
        
        return {
            "message": "School created successfully",
            "id": new_school.id,
            "name": new_school.name,
            "address": new_school.address,
            "region_id": new_school.region_id,
            "city_id": new_school.city_id,
            "district_id": new_school.district_id,
            "created_at": new_school.created_at.isoformat() if new_school.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
