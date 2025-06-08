from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Region, City, District


router = APIRouter()


class RegionBase(BaseModel):
    """Base schema for region data"""
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class RegionResponse(RegionBase):
    """Response schema for region"""
    id: int


class CityBase(BaseModel):
    """Base schema for city data"""
    name: str
    parent_region: int
    
    model_config = ConfigDict(from_attributes=True)


class CityResponse(CityBase):
    """Response schema for city"""
    id: int


class DistrictBase(BaseModel):
    """Base schema for district data"""
    name: str
    parent_region: int
    
    model_config = ConfigDict(from_attributes=True)


class DistrictResponse(DistrictBase):
    """Response schema for district"""
    id: int


class RegionDetailResponse(RegionResponse):
    """Detailed response schema for region with cities and districts"""
    cities: List[CityResponse]
    districts: List[DistrictResponse]


@router.get("/regions", response_model=List[RegionResponse])
async def get_regions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all regions"""
    regions = db.query(Region).all()
    return regions


@router.get("/regions/{region_id}", response_model=RegionDetailResponse)
async def get_region_detail(
    region_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific region including its cities and districts"""
    region = db.query(Region).filter(Region.id == region_id).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found"
        )
    
    return {
        "id": region.id,
        "name": region.name,
        "cities": region.cities,
        "districts": region.districts
    }


@router.get("/cities", response_model=List[CityResponse])
async def get_cities(
    region_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all cities, optionally filtered by region"""
    query = db.query(City)
    
    if region_id:
        query = query.filter(City.parent_region == region_id)
    
    cities = query.all()
    return cities


@router.get("/districts", response_model=List[DistrictResponse])
async def get_districts(
    region_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all districts, optionally filtered by region"""
    query = db.query(District)
    
    if region_id:
        query = query.filter(District.parent_region == region_id)
    
    districts = query.all()
    return districts


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
async def create_region(
    region_data: RegionBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new region (admin only)"""
    # Check if user is admin
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create regions"
        )
    
    # Check if region with the same name already exists
    existing_region = db.query(Region).filter(Region.name == region_data.name).first()
    if existing_region:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Region with this name already exists"
        )
    
    # Create new region
    region = Region(**region_data.dict())
    db.add(region)
    db.commit()
    db.refresh(region)
    
    return region


@router.post("/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(
    city_data: CityBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new city (admin only)"""
    # Check if user is admin
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create cities"
        )
    
    # Check if region exists
    region = db.query(Region).filter(Region.id == city_data.parent_region).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent region not found"
        )
    
    # Check if city with the same name already exists
    existing_city = db.query(City).filter(City.name == city_data.name).first()
    if existing_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City with this name already exists"
        )
    
    # Create new city
    city = City(**city_data.dict())
    db.add(city)
    db.commit()
    db.refresh(city)
    
    return city


@router.post("/districts", response_model=DistrictResponse, status_code=status.HTTP_201_CREATED)
async def create_district(
    district_data: DistrictBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new district (admin only)"""
    # Check if user is admin
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create districts"
        )
    
    # Check if region exists
    region = db.query(Region).filter(Region.id == district_data.parent_region).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent region not found"
        )
    
    # Check if district with the same name already exists
    existing_district = db.query(District).filter(District.name == district_data.name).first()
    if existing_district:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="District with this name already exists"
        )
    
    # Create new district
    district = District(**district_data.dict())
    db.add(district)
    db.commit()
    db.refresh(district)
    
    return district


@router.get("/search/locations", response_model=Dict[str, Any])
async def search_locations(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for regions, cities, and districts by name"""
    if not query or len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters long"
        )
    
    # Search for matching regions, cities, and districts
    regions = db.query(Region).filter(Region.name.ilike(f"%{query}%")).all()
    cities = db.query(City).filter(City.name.ilike(f"%{query}%")).all()
    districts = db.query(District).filter(District.name.ilike(f"%{query}%")).all()
    
    return {
        "regions": regions,
        "cities": cities,
        "districts": districts
    }


@router.get("/statistics/locations", response_model=Dict[str, Any])
async def get_location_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics about regions, cities, and districts"""
    # Check if user is admin or has appropriate permissions
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access location statistics"
        )
    
    # Count regions, cities, and districts
    region_count = db.query(Region).count()
    city_count = db.query(City).count()
    district_count = db.query(District).count()
    
    # Get regions with most cities and districts
    regions_with_counts = []
    for region in db.query(Region).all():
        city_count = len(region.cities)
        district_count = len(region.districts)
        regions_with_counts.append({
            "id": region.id,
            "name": region.name,
            "city_count": city_count,
            "district_count": district_count,
            "total_count": city_count + district_count
        })
    
    # Sort regions by total count (cities + districts)
    regions_with_counts.sort(key=lambda x: x["total_count"], reverse=True)
    
    return {
        "total_regions": region_count,
        "total_cities": city_count,
        "total_districts": district_count,
        "regions_by_location_count": regions_with_counts[:5]  # Top 5 regions
    }
