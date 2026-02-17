import pytest
from app.models.hotel import Hotel
from app.repositories.hotel import HotelRepository

@pytest.fixture
async def setup_geo_hotels():
    # Helper to create a hotel with geo location
    async def create_hotel(name, lat, lon):
        data = {
            "name": name,
            "owner_id": "geo_owner",
            "email_address": f"{name}@example.com",
            "phone_number": "1234567890",
            "state": "Lagos",
            "country": "Nigeria",
            "lga": "Ikeja",
            "is_approved": True,
            "is_open": True,
            "city": "Ikeja",
            "address": "123 Main St",
            "location": {
                "type": "Point",
                "coordinates": [lon, lat]  # Longitude first in GeoJSON
            }
        }
        hotel = Hotel(**data)
        return await HotelRepository.create_hotel(hotel)

    # Clean legacy data
    await Hotel.delete_all()

    # Create hotels at various distances from a central point (0, 0)
    # 1 degree of latitude is approx 111 km
    
    # Hotel A: At the center (0 km)
    hotel_a = await create_hotel("Hotel Center", 0.0, 0.0)
    
    # Hotel B: ~5 km away (0.045 degrees lat approx 5km)
    hotel_b = await create_hotel("Hotel 5km", 0.045, 0.0)
    
    # Hotel C: ~20 km away (0.18 degrees lat approx 20km)
    hotel_c = await create_hotel("Hotel 20km", 0.18, 0.0)
    
    yield [hotel_a, hotel_b, hotel_c]
    
    # Cleanup
    await hotel_a.delete()
    await hotel_b.delete()
    await hotel_c.delete()

@pytest.mark.anyio
async def test_geo_search_nearby(setup_geo_hotels):
    # Search from center point (0,0) with 10km radius
    # Should find Hotel Center and Hotel 5km, but not Hotel 20km
    
    hotels = await HotelRepository.get_hotels(
        skip=0,
        limit=10,
        latitude=0.0,
        longitude=0.0,
        radius_km=10.0
    )
    
    hotel_names = [h.name for h in hotels]
    assert "Hotel Center" in hotel_names
    assert "Hotel 5km" in hotel_names
    assert "Hotel 20km" not in hotel_names
    assert len(hotels) == 2

@pytest.mark.anyio
async def test_geo_search_far(setup_geo_hotels):
    # Search from center point (0,0) with 50km radius
    # Should find all three hotels
    
    hotels = await HotelRepository.get_hotels(
        skip=0,
        limit=10,
        latitude=0.0,
        longitude=0.0,
        radius_km=50.0
    )
    
    hotel_names = [h.name for h in hotels]
    assert "Hotel Center" in hotel_names
    assert "Hotel 5km" in hotel_names
    assert "Hotel 20km" in hotel_names
    assert len(hotels) == 3

@pytest.mark.anyio
async def test_geo_search_very_close(setup_geo_hotels):
    # Search from center point (0,0) with 1km radius
    # Should only find Hotel Center
    
    hotels = await HotelRepository.get_hotels(
        skip=0,
        limit=10,
        latitude=0.0,
        longitude=0.0,
        radius_km=1.0
    )
    
    hotel_names = [h.name for h in hotels]
    assert "Hotel Center" in hotel_names
    assert "Hotel 5km" not in hotel_names
    assert len(hotels) == 1
